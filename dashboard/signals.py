from django.db.models.signals import post_save
from django.dispatch import receiver
from produtos.models import Produto

@receiver(post_save, sender=Produto)
def gerar_ref_produto(sender, instance, created, **kwargs):
    """
    Gera automaticamente o campo ref do produto após salvar.
    Formato: codigo_barras(13) + descricao(160) + unidade(4) + valor(10) + estoque(10) + valor_medida(10) + categoria(10)
    
    Exemplo:
    0000000000003TEMPERO EDU GUEDES                                                                                                                                              KG  000000599000000-330400000000021
    
    Estrutura:
    - Código de barras: N 13 (Complementa zeros à esquerda)
    - Descrição: C 160 (Complementa Space à Direita)
    - Unidade: C 4 (Complementa Space à Direita)
    - Valor: N 10 (Complementa zeros à esquerda, em centavos)
    - Estoque: N 10 (Complementa zeros à esquerda, formato com sinal)
    - Valor da Medida: N 10 (Complementa zeros à esquerda, em centavos)
    - Categoria: N 10 (Complementa zeros à esquerda)
    """
    # Evita loop infinito verificando se ref já foi gerado
    if instance.ref and not created:
        return
    
    # Código de barras: N 13 (Complementa zeros à esquerda)
    codigo_barras = str(instance.id).zfill(13)
    
    # Descrição do Produto: C 160 (Complementa Space à Direita)
    descricao = instance.nome[:160].ljust(160)
    
    # Unidade: C 4 (Complementa Space à Direita)
    unidade = instance.unidade_de_medida.upper().ljust(4)
    
    # Valor do Produto: N 10 (Complementa zeros à esquerda) - em centavos
    valor = str(int(instance.valor * 100)).zfill(10)
    
    # Estoque: N 10 (Complementa zeros à esquerda) - formato com sinal
    # Exemplo: -3304 vira 000000-330 e 21 vira 0000000021
    estoque_valor = int(instance.quantidade)
    if estoque_valor < 0:
        estoque = str(estoque_valor).zfill(10)  # Mantém o sinal negativo
    else:
        estoque = str(estoque_valor).zfill(10)
    
    # Valor da Medida: N 10 (Complementa zeros à esquerda) - em centavos
    valor_medida = str(int(instance.valor_da_medida * 100)).zfill(10)
    
    # Categoria: N 10 (Complementa zeros à esquerda)
    if instance.categoria:
        categoria = str(instance.categoria.id).zfill(10)
    else:
        categoria = "0000000000"
    
    # Gera o ref completo
    ref_gerado = f"{codigo_barras}{descricao}{unidade}{valor}{estoque}{valor_medida}{categoria}"
    
    # Atualiza o campo ref sem disparar novo signal
    Produto.objects.filter(pk=instance.pk).update(ref=ref_gerado)
