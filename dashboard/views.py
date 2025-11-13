from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from produtos.models import Produto
from carrinho.models import Pedido, ItemPedido
from produtos.forms import ProdutoForm
from .forms import PedidoForm, PedidoFilterForm
from django.http import JsonResponse
import datetime

def is_staff_user(user):
    """Verifica se o usuário é staff (administrador)"""
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    """Página principal do dashboard administrativo"""
    # Estatísticas gerais
    total_produtos = Produto.objects.count()
    total_pedidos = Pedido.objects.filter(completo=True).count()
    pedidos_pendentes = Pedido.objects.filter(completo=False).count()
    
    # Pedidos recentes
    pedidos_recentes = Pedido.objects.filter(completo=True).order_by('-data_pedido')[:5]
    
    # Produtos com baixo estoque
    produtos_baixo_estoque = Produto.objects.filter(quantidade__lte=5).order_by('quantidade')[:5]
    
    context = {
        'total_produtos': total_produtos,
        'total_pedidos': total_pedidos,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_recentes': pedidos_recentes,
        'produtos_baixo_estoque': produtos_baixo_estoque,
    }
    return render(request, 'dashboard/home.html', context)

# ===== CRUD PRODUTOS =====

@login_required
@user_passes_test(is_staff_user)
def produtos_list(request):
    """Lista todos os produtos com paginação e busca"""
    search = request.GET.get('search', '')
    produtos = Produto.objects.all()
    
    if search:
        produtos = produtos.filter(
            Q(nome__icontains=search) | 
            Q(descricao__icontains=search) |
            Q(ref__icontains=search)
        )
    
    produtos = produtos.order_by('-data_criacao')
    
    paginator = Paginator(produtos, 10)  # 10 produtos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'dashboard/produtos_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def produto_create(request):
    """Criar novo produto"""
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.usuario_cadastro = request.user
            produto.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('dashboard:produtos_list')
    else:
        form = ProdutoForm()
    
    context = {'form': form, 'title': 'Criar Produto'}
    return render(request, 'dashboard/produto_form.html', context)

@login_required
@user_passes_test(is_staff_user)
def produto_update(request, pk):
    """Editar produto existente"""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('dashboard:produtos_list')
    else:
        form = ProdutoForm(instance=produto)
    
    context = {'form': form, 'title': 'Editar Produto', 'produto': produto}
    return render(request, 'dashboard/produto_form.html', context)

@login_required
@user_passes_test(is_staff_user)
def produto_delete(request, pk):
    """Deletar produto"""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto deletado com sucesso!')
        return redirect('dashboard:produtos_list')
    
    context = {'produto': produto}
    return render(request, 'dashboard/produto_confirm_delete.html', context)

# ===== CRUD PEDIDOS =====

@login_required
@user_passes_test(is_staff_user)
def pedidos_list(request):
    """Lista todos os pedidos com filtros"""
    form = PedidoFilterForm(request.GET)
    pedidos = Pedido.objects.all()
    
    # Aplicar filtros
    if form.is_valid():
        pedido_id = form.cleaned_data.get('pedido_id')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        status = form.cleaned_data.get('status')
        usuario = form.cleaned_data.get('usuario')
        
        if pedido_id:
            pedidos = pedidos.filter(id=pedido_id)
        
        if data_inicio:
            pedidos = pedidos.filter(data_pedido__date__gte=data_inicio)
        
        if data_fim:
            pedidos = pedidos.filter(data_pedido__date__lte=data_fim)
        
        if status:
            if status == 'completo':
                pedidos = pedidos.filter(completo=True)
            elif status == 'pendente':
                pedidos = pedidos.filter(completo=False)
        
        if usuario:
            pedidos = pedidos.filter(usuario__username__icontains=usuario)
    
    pedidos = pedidos.order_by('-data_pedido')
    
    paginator = Paginator(pedidos, 15)  # 15 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'dashboard/pedidos_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def pedido_detail(request, pk):
    """Visualizar detalhes do pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    itens = pedido.itempedido_set.all()
    
    context = {
        'pedido': pedido,
        'itens': itens,
    }
    return render(request, 'dashboard/pedido_detail.html', context)

@login_required
@user_passes_test(is_staff_user)
def pedido_update(request, pk):
    """Editar pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido atualizado com sucesso!')
            return redirect('dashboard:pedidos_list')
    else:
        form = PedidoForm(instance=pedido)
    
    context = {'form': form, 'title': 'Editar Pedido', 'pedido': pedido}
    return render(request, 'dashboard/pedido_form.html', context)

@login_required
@user_passes_test(is_staff_user)
def pedido_delete(request, pk):
    """Deletar pedido"""
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido deletado com sucesso!')
        return redirect('dashboard:pedidos_list')
    
    context = {'pedido': pedido}
    return render(request, 'dashboard/pedido_confirm_delete.html', context)

@login_required
@user_passes_test(is_staff_user)
def toggle_pedido_status(request, pk):
    """Alternar status do pedido (completo/pendente)"""
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pk)
        pedido.completo = not pedido.completo
        
        if pedido.completo:
            pedido.status_pagamento = 'pago'
            pedido.transaction_id = datetime.datetime.now().timestamp()
        else:
            pedido.status_pagamento = 'pendente'
            pedido.transaction_id = None
        
        pedido.save()
        
        status_text = 'finalizado' if pedido.completo else 'reaberto'
        messages.success(request, f'Pedido #{pedido.id} {status_text} com sucesso!')
        
        return JsonResponse({'success': True, 'status': pedido.completo})
    
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff_user)
def importar_produtos_ftp(request):
    """
    Importa produtos do arquivo produtos.txt via FTP
    Formato do arquivo: codigo_barras(13) + descricao(160) + unidade(4) + valor(10) + estoque(10) + valor_medida(10) + categoria(10)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        from ftplib import FTP
        from decimal import Decimal
        from produtos.models import Categoria
        
        # Configurações FTP (você pode mover isso para settings.py)
        FTP_HOST = request.POST.get('ftp_host', 'localhost')
        FTP_USER = request.POST.get('ftp_user', 'anonymous')
        FTP_PASS = request.POST.get('ftp_pass', '')
        FTP_FOLDER = '1'
        FTP_FILE = 'produtos.txt'
        
        produtos_atualizados = 0
        produtos_criados = 0
        erros = []
        
        # Conectar ao FTP
        ftp = FTP()
        ftp.connect(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        # Navegar para a pasta
        try:
            ftp.cwd(FTP_FOLDER)
        except:
            erros.append(f'Pasta "{FTP_FOLDER}" não encontrada no FTP')
            ftp.quit()
            return JsonResponse({'success': False, 'error': erros[0]})
        
        # Baixar o arquivo
        linhas = []
        def handle_line(line):
            linhas.append(line)
        
        try:
            ftp.retrlines(f'RETR {FTP_FILE}', handle_line)
        except Exception as e:
            erros.append(f'Erro ao ler arquivo "{FTP_FILE}": {str(e)}')
            ftp.quit()
            return JsonResponse({'success': False, 'error': erros[0]})
        
        ftp.quit()
        
        # Processar cada linha do arquivo
        for linha in linhas:
            if len(linha) < 217:  # 13+160+4+10+10+10+10 = 217
                erros.append(f'Linha com tamanho inválido: {len(linha)} caracteres')
                continue
            
            try:
                # Extrair campos conforme posições
                codigo_barras = linha[0:13].strip()
                descricao = linha[13:173].strip()
                unidade = linha[173:177].strip().lower()
                valor_centavos = linha[177:187].strip()
                estoque = linha[187:197].strip()
                valor_medida_centavos = linha[197:207].strip()
                categoria_id = linha[207:217].strip()
                
                # Converter valores
                produto_id = int(codigo_barras)
                valor = Decimal(valor_centavos) / 100
                quantidade = int(estoque)
                valor_medida = Decimal(valor_medida_centavos) / 100
                
                # Buscar categoria
                categoria = None
                if categoria_id and categoria_id != '0000000000':
                    try:
                        categoria = Categoria.objects.get(id=int(categoria_id))
                    except Categoria.DoesNotExist:
                        pass
                
                # Atualizar ou criar produto
                produto, created = Produto.objects.update_or_create(
                    id=produto_id,
                    defaults={
                        'nome': descricao,
                        'valor': valor,
                        'quantidade': quantidade,
                        'unidade_de_medida': unidade,
                        'valor_da_medida': valor_medida,
                        'categoria': categoria,
                    }
                )
                
                if created:
                    produtos_criados += 1
                else:
                    produtos_atualizados += 1
                    
            except Exception as e:
                erros.append(f'Erro ao processar linha: {str(e)}')
                continue
        
        # Preparar mensagem de resultado
        mensagem = f'Importação concluída! {produtos_criados} produtos criados, {produtos_atualizados} produtos atualizados.'
        if erros:
            mensagem += f' {len(erros)} erros encontrados.'
        
        messages.success(request, mensagem)
        
        return JsonResponse({
            'success': True,
            'produtos_criados': produtos_criados,
            'produtos_atualizados': produtos_atualizados,
            'erros': erros[:10]  # Retorna apenas os primeiros 10 erros
        })
        
    except Exception as e:
        error_msg = f'Erro na importação FTP: {str(e)}'
        messages.error(request, error_msg)
        return JsonResponse({'success': False, 'error': error_msg})
