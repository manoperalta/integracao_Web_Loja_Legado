from django.db import models
from django.contrib.auth.models import User
from produtos.models import Produto

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_pedido = models.DateTimeField(auto_now_add=True)
    completo = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    status_pagamento = models.CharField(max_length=20, default='pendente') # Adicionado campo de status de pagamento

    def __str__(self):
        return str(self.id)

    @property
    def get_carrinho_total(self):
        itempedidos = self.itempedido_set.all()
        total = sum([item.get_total for item in itempedidos])
        return total

    @property
    def get_carrinho_itens(self):
        itempedidos = self.itempedido_set.all()
        total = sum([item.quantidade for item in itempedidos])
        return total

class ItemPedido(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)
    quantidade = models.IntegerField(default=0, null=True, blank=True)
    data_adicao = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        if self.produto is None:
            return 0
        total = self.produto.valor * self.quantidade
        return total

