from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido, ItemPedido
from produtos.models import Produto
import os
from .ftp_util import enviar_ftp  # Importe a função de envio FTP (criada separadamente)
from .sftp_util import enviar_sftp

def atualizar_ref_produto(produto):
    """
    Atualiza o campo ref do produto seguindo os padrões do dashboard/signals.py
    Formato: codigo_barras(13) + descricao(160) + unidade(4) + valor(10) + estoque(10) + valor_medida(10) + categoria(10)
    """
    # Código de barras: N 13 (Complementa zeros à esquerda)
    codigo_barras = str(produto.id).zfill(13)
    
    # Descrição do Produto: C 160 (Complementa Space à Direita)
    descricao = produto.nome[:160].ljust(160)
    
    # Unidade: C 4 (Complementa Space à Direita)
    unidade = produto.unidade_de_medida.upper().ljust(4)
    
    # Valor do Produto: N 10 (Complementa zeros à esquerda) - em centavos
    valor = str(int(produto.valor * 100)).zfill(10)
    
    # Estoque: N 10 (Complementa zeros à esquerda) - formato com sinal
    estoque_valor = int(produto.quantidade)
    if estoque_valor < 0:
        estoque = str(estoque_valor).zfill(10)  # Mantém o sinal negativo
    else:
        estoque = str(estoque_valor).zfill(10)
    
    # Valor da Medida: N 10 (Complementa zeros à esquerda) - em centavos
    valor_medida = str(int(produto.valor_da_medida * 100)).zfill(10)
    
    # Categoria: N 10 (Complementa zeros à esquerda)
    if produto.categoria:
        categoria = str(produto.categoria.id).zfill(10)
    else:
        categoria = "0000000000"
    
    # Gera o ref completo
    ref_gerado = f"{codigo_barras}{descricao}{unidade}{valor}{estoque}{valor_medida}{categoria}"
    
    # Atualiza o campo ref sem disparar novo signal
    Produto.objects.filter(pk=produto.pk).update(ref=ref_gerado)
    
    return ref_gerado

@receiver(post_save, sender=ItemPedido)
def atualizar_estoque_e_ref(sender, instance, created, **kwargs):
    """
    Atualiza o estoque do produto quando um item do pedido é salvo/atualizado
    e regenera o ref do produto com o novo estoque.
    """
    if instance.produto and instance.pedido and instance.pedido.completo:
        # Atualiza o estoque do produto (subtrai a quantidade do pedido)
        produto = instance.produto
        produto.quantidade -= instance.quantidade
        produto.save()
        
        # Atualiza o ref do produto com o novo estoque
        atualizar_ref_produto(produto)

@receiver(post_save, sender=Pedido)
def gerar_arquivo_pedido(sender, instance, created, **kwargs):
    """
    Gera arquivo txt com os dados do campo ref dos produtos quando o pedido é marcado como completo.
    Cada produto é separado por uma linha em branco.
    """
    if instance.completo and not created:
        # Diretório onde o arquivo será salvo antes de enviar
        pedidos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pedidos')
        os.makedirs(pedidos_dir, exist_ok=True)

        # Nome do arquivo
        nome_arquivo = os.path.join(pedidos_dir, f'pedido_{instance.id}.txt')

        # Criação do conteúdo do pedido
        with open(nome_arquivo, 'w') as f:
            itens = instance.itempedido_set.all()
            
            for index, item in enumerate(itens):
                if item.produto and item.produto.ref:
                    # Escreve o ref do produto
                    f.write(f'{item.produto.ref}\n')
                    
                    # Adiciona linha em branco entre produtos (exceto após o último)
                    if index < len(itens) - 1:
                        f.write('\n')

        # Enviar o arquivo via FTP após criação
        enviar_ftp(nome_arquivo)
        
        # Enviar o arquivo via SFTP 
        # enviar_sftp(nome_arquivo)
