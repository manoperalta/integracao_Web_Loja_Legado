from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from produtos.models import Produto, Categoria
from django.http import JsonResponse
from ftplib import FTP, error_perm
from decimal import Decimal
import socket
import io
from .models import FTPConfig

def is_staff_user(user):
    """Verifica se o usuário é staff (administrador)"""
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def wizard_inicio(request):
    """Página inicial do wizard - Etapa 1: Importar Categorias"""
    # Verificar se existe configuração FTP ativa
    ftp_config = FTPConfig.get_config_ativa()
    
    if not ftp_config:
        messages.error(request, 'Nenhuma configuração FTP ativa encontrada. Por favor, configure o servidor FTP no painel administrativo.')
        return redirect('dashboard:home')
    
    context = {
        'ftp_config': ftp_config
    }
    return render(request, 'import/wizard_categorias.html', context)

@login_required
@user_passes_test(is_staff_user)
def importar_categorias_ftp(request):
    """
    Importa categorias do arquivo CATEGORIAS.TXT via FTP
    Formato do arquivo: 111 caracteres por linha
    - 9 caracteres: ID da categoria (ex: 000000001)
    - 102 caracteres: Nome da categoria com espaços à direita
    Encoding: ISO-8859-1 (Latin-1)
    Exemplo: 000000001CASTANHAS                                                                                           
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    ftp = None
    try:
        # Buscar configuração FTP ativa
        ftp_config = FTPConfig.get_config_ativa()
        
        if not ftp_config:
            return JsonResponse({'success': False, 'error': 'Nenhuma configuração FTP ativa encontrada. Configure no painel administrativo.'})
        
        # Validar campos obrigatórios
        if not ftp_config.host or not ftp_config.host.strip():
            return JsonResponse({
                'success': False, 
                'error': 'Host FTP não configurado ou está vazio. Acesse o painel administrativo em /admin/import/ftpconfig/ e configure o campo "Host FTP" com o endereço do servidor (ex: ftp.seuservidor.com.br)'
            })
        
        if not ftp_config.usuario or not ftp_config.usuario.strip():
            return JsonResponse({
                'success': False, 
                'error': 'Usuário FTP não configurado ou está vazio. Acesse o painel administrativo e configure o campo "Usuário".'
            })
        
        # Salvar flag na sessão indicando que categorias foram importadas
        request.session['categorias_importadas'] = True
        
        categorias_criadas = 0
        categorias_atualizadas = 0
        erros = []
        
        # Conectar ao FTP usando configuração centralizada
        try:
            ftp = FTP()
            host_limpo = ftp_config.host.strip()
            usuario_limpo = ftp_config.usuario.strip()
            
            ftp.connect(host_limpo, ftp_config.porta, timeout=30)
            ftp.login(usuario_limpo, ftp_config.senha)
        except socket.gaierror as e:
            return JsonResponse({
                'success': False, 
                'error': f'Não foi possível resolver o endereço do servidor FTP "{ftp_config.host}". Verifique se o host está correto no painel administrativo. Detalhes: {str(e)}'
            })
        except socket.timeout:
            return JsonResponse({
                'success': False, 
                'error': f'Tempo esgotado ao tentar conectar ao servidor FTP "{ftp_config.host}". Verifique se o servidor está acessível e se a porta {ftp_config.porta} está correta.'
            })
        except error_perm as e:
            return JsonResponse({
                'success': False, 
                'error': f'Erro de autenticação FTP: {str(e)}. Verifique usuário e senha no painel administrativo.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Erro ao conectar ao FTP: {str(e)}'
            })
        
        # Navegar para a pasta se especificada
        if ftp_config.diretorio and ftp_config.diretorio.strip():
            try:
                ftp.cwd(ftp_config.diretorio.strip())
            except error_perm as e:
                if ftp:
                    ftp.quit()
                return JsonResponse({
                    'success': False, 
                    'error': f'Pasta "{ftp_config.diretorio}" não encontrada no FTP. Verifique se o diretório existe ou deixe o campo vazio para usar a raiz.'
                })
            except Exception as e:
                if ftp:
                    ftp.quit()
                return JsonResponse({
                    'success': False, 
                    'error': f'Erro ao acessar pasta "{ftp_config.diretorio}": {str(e)}'
                })
        
        # Baixar o arquivo de categorias em modo binário e decodificar com ISO-8859-1
        buffer = io.BytesIO()
        
        try:
            ftp.retrbinary('RETR CATEGORIAS.TXT', buffer.write)
        except error_perm as e:
            if ftp:
                ftp.quit()
            return JsonResponse({
                'success': False, 
                'error': f'Arquivo "CATEGORIAS.TXT" não encontrado no servidor FTP. Verifique se o arquivo existe no diretório "{ftp_config.diretorio or "raiz"}".'
            })
        except Exception as e:
            if ftp:
                ftp.quit()
            return JsonResponse({
                'success': False, 
                'error': f'Erro ao ler arquivo "CATEGORIAS.TXT": {str(e)}'
            })
        
        if ftp:
            ftp.quit()
        
        # Decodificar conteúdo com ISO-8859-1
        buffer.seek(0)
        conteudo = buffer.read().decode('iso-8859-1')
        linhas = conteudo.split('\n')
        
        # Processar cada linha do arquivo
        for idx, linha in enumerate(linhas, 1):
            # Remover caracteres de controle (CR/LF do Windows)
            linha = linha.replace('\r', '').replace('\n', '').strip()
            
            # Ignorar linhas vazias
            if not linha:
                continue
            
            # Verificar tamanho mínimo (9 caracteres para ID)
            if len(linha) < 9:
                erros.append(f'Linha {idx}: tamanho inválido ({len(linha)} caracteres, mínimo 9)')
                continue
            
            try:
                # Extrair campos
                # Formato: 9 dígitos (ID) + resto (nome)
                categoria_id = linha[0:9].strip()
                nome = linha[9:].strip()
                
                if not categoria_id:
                    erros.append(f'Linha {idx}: ID da categoria vazio')
                    continue
                
                if not nome:
                    erros.append(f'Linha {idx}: Nome da categoria vazio')
                    continue
                
                # Converter ID
                try:
                    cat_id = int(categoria_id)
                except ValueError:
                    erros.append(f'Linha {idx}: ID inválido "{categoria_id}"')
                    continue
                
                # Atualizar ou criar categoria
                categoria, created = Categoria.objects.update_or_create(
                    id=cat_id,
                    defaults={'nome': nome}
                )
                
                if created:
                    categorias_criadas += 1
                else:
                    categorias_atualizadas += 1
                    
            except Exception as e:
                erros.append(f'Linha {idx}: Erro ao processar - {str(e)}')
                continue
        
        # Preparar mensagem de resultado
        mensagem = f'Importação de categorias concluída! {categorias_criadas} categorias criadas, {categorias_atualizadas} categorias atualizadas.'
        if erros:
            mensagem += f' {len(erros)} erros encontrados.'
        
        return JsonResponse({
            'success': True,
            'categorias_criadas': categorias_criadas,
            'categorias_atualizadas': categorias_atualizadas,
            'erros': erros[:10],
            'mensagem': mensagem
        })
        
    except Exception as e:
        if ftp:
            try:
                ftp.quit()
            except:
                pass
        error_msg = f'Erro na importação FTP de categorias: {str(e)}'
        return JsonResponse({'success': False, 'error': error_msg})

@login_required
@user_passes_test(is_staff_user)
def wizard_produtos(request):
    """Página do wizard - Etapa 2: Importar Produtos"""
    # Verificar se passou pela etapa 1
    if not request.session.get('categorias_importadas'):
        messages.warning(request, 'Por favor, importe as categorias primeiro.')
        return redirect('import:wizard_inicio')
    
    # Verificar se existe configuração FTP ativa
    ftp_config = FTPConfig.get_config_ativa()
    
    if not ftp_config:
        messages.error(request, 'Nenhuma configuração FTP ativa encontrada. Por favor, configure o servidor FTP no painel administrativo.')
        return redirect('dashboard:home')
    
    context = {
        'ftp_config': ftp_config
    }
    return render(request, 'import/wizard_produtos.html', context)

@login_required
@user_passes_test(is_staff_user)
def importar_produtos_ftp(request):
    """
    Importa produtos do arquivo PRODUTOS.TXT via FTP
    Formato do arquivo: 207 caracteres por linha (sem categoria no arquivo)
    - 13 caracteres: código de barras (ID do produto)
    - 160 caracteres: descrição
    - 4 caracteres: unidade de medida
    - 10 caracteres: valor em centavos
    - 10 caracteres: estoque (com sinal)
    - 10 caracteres: valor da medida em centavos
    Encoding: ISO-8859-1 (Latin-1)
    Nota: Categoria não está presente no arquivo, será definida como NULL
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    ftp = None
    try:
        # Buscar configuração FTP ativa
        ftp_config = FTPConfig.get_config_ativa()
        
        if not ftp_config:
            return JsonResponse({'success': False, 'error': 'Nenhuma configuração FTP ativa encontrada. Configure no painel administrativo.'})
        
        # Validar campos obrigatórios
        if not ftp_config.host or not ftp_config.host.strip():
            return JsonResponse({
                'success': False, 
                'error': 'Host FTP não configurado ou está vazio. Acesse o painel administrativo em /admin/import/ftpconfig/ e configure o campo "Host FTP".'
            })
        
        if not ftp_config.usuario or not ftp_config.usuario.strip():
            return JsonResponse({
                'success': False, 
                'error': 'Usuário FTP não configurado ou está vazio. Acesse o painel administrativo e configure o campo "Usuário".'
            })
        
        produtos_atualizados = 0
        produtos_criados = 0
        erros = []
        
        # Conectar ao FTP usando configuração centralizada
        try:
            ftp = FTP()
            host_limpo = ftp_config.host.strip()
            usuario_limpo = ftp_config.usuario.strip()
            
            ftp.connect(host_limpo, ftp_config.porta, timeout=30)
            ftp.login(usuario_limpo, ftp_config.senha)
        except socket.gaierror as e:
            return JsonResponse({
                'success': False, 
                'error': f'Não foi possível resolver o endereço do servidor FTP "{ftp_config.host}". Verifique se o host está correto no painel administrativo.'
            })
        except socket.timeout:
            return JsonResponse({
                'success': False, 
                'error': f'Tempo esgotado ao tentar conectar ao servidor FTP "{ftp_config.host}". Verifique se o servidor está acessível.'
            })
        except error_perm as e:
            return JsonResponse({
                'success': False, 
                'error': f'Erro de autenticação FTP: {str(e)}. Verifique usuário e senha.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Erro ao conectar ao FTP: {str(e)}'
            })
        
        # Navegar para a pasta se especificada
        if ftp_config.diretorio and ftp_config.diretorio.strip():
            try:
                ftp.cwd(ftp_config.diretorio.strip())
            except error_perm as e:
                if ftp:
                    ftp.quit()
                return JsonResponse({
                    'success': False, 
                    'error': f'Pasta "{ftp_config.diretorio}" não encontrada no FTP.'
                })
            except Exception as e:
                if ftp:
                    ftp.quit()
                return JsonResponse({
                    'success': False, 
                    'error': f'Erro ao acessar pasta "{ftp_config.diretorio}": {str(e)}'
                })
        
        # Baixar o arquivo em modo binário e decodificar com ISO-8859-1
        buffer = io.BytesIO()
        
        try:
            ftp.retrbinary('RETR PRODUTOS.TXT', buffer.write)
        except error_perm as e:
            if ftp:
                ftp.quit()
            return JsonResponse({
                'success': False, 
                'error': f'Arquivo "PRODUTOS.TXT" não encontrado no servidor FTP.'
            })
        except Exception as e:
            if ftp:
                ftp.quit()
            return JsonResponse({
                'success': False, 
                'error': f'Erro ao ler arquivo "PRODUTOS.TXT": {str(e)}'
            })
        
        if ftp:
            ftp.quit()
        
        # Decodificar conteúdo com ISO-8859-1
        buffer.seek(0)
        conteudo = buffer.read().decode('iso-8859-1')
        linhas = conteudo.split('\n')
        
        # Processar cada linha do arquivo
        for idx, linha in enumerate(linhas, 1):
            # Remover caracteres de controle (CR/LF do Windows)
            linha = linha.replace('\r', '').replace('\n', '').strip()
            
            # Ignorar linhas vazias
            if not linha:
                continue
            
            # Verificar tamanho mínimo (207 caracteres)
            if len(linha) < 207:
                erros.append(f'Linha {idx}: tamanho inválido ({len(linha)} caracteres, esperado 207)')
                continue
            
            try:
                # Extrair campos conforme posições
                codigo_barras = linha[0:13].strip()
                descricao = linha[13:173].strip()
                unidade = linha[173:177].strip().lower()
                valor_centavos = linha[177:187].strip()
                estoque = linha[187:197].strip()
                valor_medida_centavos = linha[197:207].strip()
                
                # Validar campos obrigatórios
                if not codigo_barras:
                    erros.append(f'Linha {idx}: Código de barras vazio')
                    continue
                
                if not descricao:
                    erros.append(f'Linha {idx}: Descrição vazia')
                    continue
                
                # Converter valores
                try:
                    produto_id = int(codigo_barras)
                except ValueError:
                    erros.append(f'Linha {idx}: Código de barras inválido "{codigo_barras}"')
                    continue
                
                try:
                    valor = Decimal(valor_centavos) / 100
                except:
                    erros.append(f'Linha {idx}: Valor inválido "{valor_centavos}"')
                    continue
                
                try:
                    # Tratar estoque com sinal negativo
                    quantidade = int(estoque.replace('-', ''))
                except:
                    erros.append(f'Linha {idx}: Estoque inválido "{estoque}"')
                    continue
                
                try:
                    valor_medida = Decimal(valor_medida_centavos) / 100
                except:
                    erros.append(f'Linha {idx}: Valor da medida inválido "{valor_medida_centavos}"')
                    continue
                
                # Categoria não está no arquivo, será NULL
                categoria = None
                
                # Atualizar ou criar produto
                produto, created = Produto.objects.update_or_create(
                    id=produto_id,
                    defaults={
                        'nome': descricao,
                        'valor': valor,
                        'quantidade': quantidade,
                        'unidade_de_medida': unidade if unidade else 'kg',
                        'valor_da_medida': valor_medida,
                        'categoria': categoria,
                    }
                )
                
                if created:
                    produtos_criados += 1
                else:
                    produtos_atualizados += 1
                    
            except Exception as e:
                erros.append(f'Linha {idx}: Erro ao processar - {str(e)}')
                continue
        
        # Preparar mensagem de resultado
        mensagem = f'Importação de produtos concluída! {produtos_criados} produtos criados, {produtos_atualizados} produtos atualizados.'
        if erros:
            mensagem += f' {len(erros)} erros encontrados.'
        
        # Limpar sessão após importação completa
        if 'categorias_importadas' in request.session:
            del request.session['categorias_importadas']
        
        return JsonResponse({
            'success': True,
            'produtos_criados': produtos_criados,
            'produtos_atualizados': produtos_atualizados,
            'erros': erros[:10],
            'mensagem': mensagem
        })
        
    except Exception as e:
        if ftp:
            try:
                ftp.quit()
            except:
                pass
        error_msg = f'Erro na importação FTP de produtos: {str(e)}'
        return JsonResponse({'success': False, 'error': error_msg})
