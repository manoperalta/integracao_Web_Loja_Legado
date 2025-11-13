from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Categoria
from .forms import CategoriaForm

# Views para Categoria
@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'produtos/lista_categorias.html', {'categorias': categorias})

@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'produtos/criar_categoria.html', {'form': form})

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'produtos/editar_categoria.html', {'form': form, 'categoria': categoria})

@login_required
def deletar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categorias')
    return render(request, 'produtos/confirmar_delete_categoria.html', {'categoria': categoria})

@login_required
@require_POST
def criar_categoria_ajax(request):
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({'success': False, 'error': 'Nome da categoria é obrigatório'})
        
        # Verificar se já existe
        if Categoria.objects.filter(nome=nome).exists():
            return JsonResponse({'success': False, 'error': 'Categoria já existe'})
        
        # Criar categoria
        categoria = Categoria.objects.create(nome=nome)
        
        return JsonResponse({
            'success': True,
            'categoria': {
                'id': categoria.id,
                'nome': categoria.nome
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
