from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido
import os
from .ftp_util import enviar_ftp  # Importe a função de envio FTP (criada separadamente)
from .sftp_util import enviar_sftp

@receiver(post_save, sender=Pedido)
def gerar_arquivo_pedido(sender, instance, created, **kwargs):
    if instance.completo and not created:
        # Diretório onde o arquivo será salvo antes de enviar
        pedidos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pedidos')
        os.makedirs(pedidos_dir, exist_ok=True)

        # Nome do arquivo
        nome_arquivo = os.path.join(pedidos_dir, f'pedido_{instance.id}.txt')

        # Criação do conteúdo do pedido
        with open(nome_arquivo, 'w') as f:
            f.write(f'Detalhes do Pedido #{instance.id}\n')
            f.write(f'Data do Pedido: {instance.data_pedido}\n')
            f.write(f'Cliente: {instance.usuario.username if instance.usuario else "Convidado"}\n')
            f.write(f'Status do Pagamento: {instance.status_pagamento}\n')
            f.write(f'Transaction ID: {instance.transaction_id}\n\n')
            f.write('Produtos:\n')
            for item in instance.itempedido_set.all():
                f.write(f'  - ID: {item.produto.id}\n')
                f.write(f'    Nome: {item.produto.nome}\n')
                f.write(f'    Descrição: {item.produto.descricao}\n')
                f.write(f'    Quantidade: {item.quantidade}\n')
                f.write(f'    Preço Unitário: R${item.produto.valor:.2f}\n')
                f.write(f'    Total do Item: R${item.get_total:.2f}\n')
            f.write(f'\nTotal do Pedido: R${instance.get_carrinho_total:.2f}\n')

        # Enviar o arquivo via FTP após criação
        enviar_ftp(nome_arquivo)
        
        # Enviar o arquivo via SFTP 

        # enviar_sftp(nome_arquivo)

