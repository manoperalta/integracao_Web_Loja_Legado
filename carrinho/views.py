from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from produtos.models import Produto
from .models import Pedido, ItemPedido
from django.http import JsonResponse
import json
import datetime

def home(request):
    if request.user.is_authenticated:
        cliente = request.user
        pedido, created = Pedido.objects.get_or_create(usuario=cliente, completo=False)
        carrinho_itens = pedido.get_carrinho_itens
    else:
        carrinho_itens = 0

    produtos = Produto.objects.all()
    context = {"produtos": produtos, "carrinho_itens": carrinho_itens}
    return render(request, "carrinho/home.html", context)

def carrinho(request):
    if request.user.is_authenticated:
        cliente = request.user
        pedido, created = Pedido.objects.get_or_create(usuario=cliente, completo=False)
        itens = pedido.itempedido_set.all()
        carrinho_itens = pedido.get_carrinho_itens
    else:
        # Criar um carrinho vazio para usuários não autenticados
        itens = []
        pedido = {"get_carrinho_total": 0, "get_carrinho_itens": 0}
        carrinho_itens = pedido["get_carrinho_itens"]
    context = {"itens": itens, "pedido": pedido, "carrinho_itens": carrinho_itens}
    return render(request, "carrinho/carrinho.html", context)

def checkout(request):
    if request.user.is_authenticated:
        cliente = request.user
        pedido, created = Pedido.objects.get_or_create(usuario=cliente, completo=False)
        itens = pedido.itempedido_set.all()
        carrinho_itens = pedido.get_carrinho_itens
    else:
        itens = []
        pedido = {"get_carrinho_total": 0, "get_carrinho_itens": 0}
        carrinho_itens = pedido["get_carrinho_itens"]
    context = {"itens": itens, "pedido": pedido, "carrinho_itens": carrinho_itens}
    return render(request, "carrinho/checkout.html", context)



def fechar_pedido(request):
    if request.user.is_authenticated:
        cliente = request.user
        pedido = Pedido.objects.filter(usuario=cliente, completo=False).first()
        if pedido and pedido.get_carrinho_itens > 0:
            pedido.completo = True
            pedido.status_pagamento = 'pago'
            pedido.transaction_id = datetime.datetime.now().timestamp() # Gerar um transaction_id
            pedido.save() # O signal será acionado aqui para gerar o TXT
            
            # Adicionar mensagem de sucesso
            from django.contrib import messages
            messages.success(request, f'Pedido #{pedido.id} finalizado com sucesso! Arquivo de pedido gerado.')
            return redirect("home") # Redirecionar para a home ou uma página de confirmação
        elif pedido and pedido.get_carrinho_itens == 0:
            from django.contrib import messages
            messages.warning(request, 'Não é possível finalizar um pedido vazio.')
            return redirect("carrinho")
        else:
            from django.contrib import messages
            messages.info(request, 'Nenhum pedido encontrado para finalizar.')
            return redirect("carrinho")
    else:
        from django.contrib import messages
        messages.error(request, 'Você precisa estar logado para finalizar um pedido.')
        return redirect("login")

def get_cart_count(request):
    """Retorna a contagem de itens no carrinho via AJAX"""
    if request.user.is_authenticated:
        pedido, created = Pedido.objects.get_or_create(usuario=request.user, completo=False)
        cart_count = pedido.get_carrinho_itens
    else:
        cart_count = 0
    
    return JsonResponse({'cart_count': cart_count})

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        cliente = request.user
        pedido, created = Pedido.objects.get_or_create(usuario=cliente, completo=False)
        total = float(data["form"]["total"])
        pedido.transaction_id = transaction_id

        if total == pedido.get_carrinho_total:
            pedido.completo = True
            pedido.status_pagamento = 'pago'
        pedido.save()
    else:
        print("Usuário não logado...")
    return JsonResponse("Pagamento completo!", safe=False)


def atualizar_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data["produtoId"]
        action = data["action"]

        print('Produto:', product_id, 'Ação:', action)

        usuario = request.user
        produto = Produto.objects.get(id=product_id)
        pedido, created = Pedido.objects.get_or_create(usuario=usuario, completo=False)
        item_pedido, created = ItemPedido.objects.get_or_create(pedido=pedido, produto=produto)

        if action == 'add':
            item_pedido.quantidade += 1
        elif action == 'remove':
            item_pedido.quantidade -= 1

        # Se a quantidade for 0 ou menos, remove o item
        if item_pedido.quantidade <= 0:
            item_pedido.delete()
        else:
            item_pedido.save()  # <-- grava no banco!

        # Atualiza o resumo do carrinho
        data = {
            'quantidade': item_pedido.quantidade if item_pedido.id else 0,
            'item_total': item_pedido.get_total if item_pedido.id else 0,
            'carrinho_itens': pedido.get_carrinho_itens,
                            'carrinho_total': float(pedido.get_carrinho_total) if pedido.get_carrinho_total else 0,
        }

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Método inválido'}, status=400)