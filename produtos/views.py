from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json
from .models import Categoria, Produto
from .forms import CategoriaForm

def is_staff_user(user):
    """Verifica se o usuário é staff (administrador)"""
    return user.is_staff

# ============================================================================
# VIEWS PARA CATEGORIA
# ============================================================================

@login_required
@user_passes_test(is_staff_user)
def lista_categorias(request):
    """
    Lista todas as categorias com paginação, busca e filtros
    """
    # Buscar todas as categorias com contagem de produtos
    categorias = Categoria.objects.annotate(
        total_produtos=Count('produtos')
    ).order_by('-data_criacao')
    
    # Filtro de busca
    busca = request.GET.get('busca', '').strip()
    if busca:
        categorias = categorias.filter(
            Q(nome__icontains=busca) | 
            Q(id__icontains=busca)
        )
    
    # Paginação
    paginator = Paginator(categorias, 20)  # 20 categorias por página
    page_number = request.GET.get('page', 1)
    
    try:
        categorias_paginadas = paginator.page(page_number)
    except:
        categorias_paginadas = paginator.page(1)
    
    context = {
        'categorias': categorias_paginadas,
        'busca': busca,
        'total_categorias': categorias.count()
    }
    
    return render(request, 'produtos/lista_categorias.html', context)

@login_required
@user_passes_test(is_staff_user)
def criar_categoria(request):
    """
    Cria uma nova categoria
    """
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        
        if form.is_valid():
            try:
                nome = form.cleaned_data['nome'].strip()
                
                # Verificar se já existe categoria com esse nome
                if Categoria.objects.filter(nome__iexact=nome).exists():
                    messages.error(request, f'Já existe uma categoria com o nome "{nome}".')
                    return render(request, 'produtos/criar_categoria.html', {'form': form})
                
                # Criar categoria
                categoria = form.save(commit=False)
                categoria.nome = nome
                categoria.save()
                
                messages.success(request, f'Categoria "{categoria.nome}" criada com sucesso!')
                return redirect('lista_categorias')
                
            except Exception as e:
                messages.error(request, f'Erro ao criar categoria: {str(e)}')
                return render(request, 'produtos/criar_categoria.html', {'form': form})
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CategoriaForm()
    
    return render(request, 'produtos/criar_categoria.html', {'form': form})

@login_required
@user_passes_test(is_staff_user)
def editar_categoria(request, pk):
    """
    Edita uma categoria existente
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    nome_original = categoria.nome
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        
        if form.is_valid():
            try:
                nome_novo = form.cleaned_data['nome'].strip()
                
                # Verificar se já existe outra categoria com esse nome
                if Categoria.objects.filter(nome__iexact=nome_novo).exclude(pk=pk).exists():
                    messages.error(request, f'Já existe outra categoria com o nome "{nome_novo}".')
                    return render(request, 'produtos/editar_categoria.html', {
                        'form': form, 
                        'categoria': categoria
                    })
                
                # Atualizar categoria
                categoria = form.save(commit=False)
                categoria.nome = nome_novo
                categoria.save()
                
                messages.success(request, f'Categoria "{nome_original}" atualizada para "{categoria.nome}" com sucesso!')
                return redirect('lista_categorias')
                
            except Exception as e:
                messages.error(request, f'Erro ao atualizar categoria: {str(e)}')
                return render(request, 'produtos/editar_categoria.html', {
                    'form': form, 
                    'categoria': categoria
                })
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CategoriaForm(instance=categoria)
    
    # Contar produtos vinculados
    total_produtos = categoria.produtos.count()
    
    context = {
        'form': form,
        'categoria': categoria,
        'total_produtos': total_produtos
    }
    
    return render(request, 'produtos/editar_categoria.html', context)

@login_required
@user_passes_test(is_staff_user)
def deletar_categoria(request, pk):
    """
    Deleta uma categoria (apenas se não tiver produtos vinculados)
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    
    # Verificar se há produtos vinculados
    total_produtos = categoria.produtos.count()
    
    if request.method == 'POST':
        if total_produtos > 0:
            messages.error(
                request, 
                f'Não é possível deletar a categoria "{categoria.nome}" pois existem {total_produtos} produto(s) vinculado(s). '
                f'Remova ou reatribua os produtos antes de deletar a categoria.'
            )
            return redirect('lista_categorias')
        
        try:
            nome_categoria = categoria.nome
            categoria.delete()
            messages.success(request, f'Categoria "{nome_categoria}" deletada com sucesso!')
            return redirect('lista_categorias')
        except Exception as e:
            messages.error(request, f'Erro ao deletar categoria: {str(e)}')
            return redirect('lista_categorias')
    
    context = {
        'categoria': categoria,
        'total_produtos': total_produtos
    }
    
    return render(request, 'produtos/confirmar_delete_categoria.html', context)

@login_required
@user_passes_test(is_staff_user)
@require_POST
def criar_categoria_ajax(request):
    """
    Cria uma nova categoria via AJAX (para uso em modais/formulários dinâmicos)
    """
    try:
        # Parsear dados JSON
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        # Validar nome
        if not nome:
            return JsonResponse({
                'success': False, 
                'error': 'Nome da categoria é obrigatório'
            })
        
        if len(nome) < 2:
            return JsonResponse({
                'success': False, 
                'error': 'Nome da categoria deve ter pelo menos 2 caracteres'
            })
        
        if len(nome) > 100:
            return JsonResponse({
                'success': False, 
                'error': 'Nome da categoria deve ter no máximo 100 caracteres'
            })
        
        # Verificar se já existe
        if Categoria.objects.filter(nome__iexact=nome).exists():
            return JsonResponse({
                'success': False, 
                'error': f'Já existe uma categoria com o nome "{nome}"'
            })
        
        # Criar categoria
        categoria = Categoria.objects.create(nome=nome)
        
        return JsonResponse({
            'success': True,
            'mensagem': f'Categoria "{categoria.nome}" criada com sucesso!',
            'categoria': {
                'id': categoria.id,
                'nome': categoria.nome,
                'codigo': categoria.get_codigo(),
                'codigo_completo': categoria.get_codigo_completo()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'Dados JSON inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Erro ao criar categoria: {str(e)}'
        })

@login_required
@user_passes_test(is_staff_user)
def detalhes_categoria(request, pk):
    """
    Exibe detalhes de uma categoria e seus produtos
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    
    # Buscar produtos da categoria
    produtos = categoria.produtos.all().order_by('-data_criacao')
    
    # Paginação de produtos
    paginator = Paginator(produtos, 20)
    page_number = request.GET.get('page', 1)
    
    try:
        produtos_paginados = paginator.page(page_number)
    except:
        produtos_paginados = paginator.page(1)
    
    context = {
        'categoria': categoria,
        'produtos': produtos_paginados,
        'total_produtos': produtos.count()
    }
    
    return render(request, 'produtos/detalhes_categoria.html', context)
