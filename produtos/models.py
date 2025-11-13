from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
    def __str__(self):
        return f"{str(self.id).zfill(9)}{self.nome}"
    
    def get_codigo(self):
        """Retorna o código formatado com 9 dígitos"""
        return str(self.id).zfill(9)
    
    def get_codigo_completo(self):
        """Retorna código + nome (ex: 000000002TEMPEROS)"""
        return f"{self.get_codigo()}{self.nome}"

class Produto(models.Model):
    UNIDADES_MEDIDA = [
        ('mg', 'Miligrama (mg)'),
        ('g', 'Grama (g)'),
        ('kg', 'Quilograma (kg)'),
        ('mm', 'Milímetro (mm)'),
        ('cm', 'Centímetro (cm)'),
        ('m', 'Metro (m)'),
        ('km', 'Quilômetro (km)'),
        ('ml', 'Mililitro (ml)'),
        ('l', 'Litro (l)'),
    ]
    
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    quantidade = models.IntegerField(default=0)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos_imagens/', blank=True, null=True, default='produtos_imagens/placeholder.png')
    ref = models.CharField(max_length=250, unique=True, blank=True, null=True)
    unidade_de_medida = models.CharField(max_length=2, choices=UNIDADES_MEDIDA, default='kg')
    valor_da_medida = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')
    usuario_cadastro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos_cadastrados')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome


