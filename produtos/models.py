from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome da Categoria",
        help_text="Nome da categoria (ex: CASTANHAS, TEMPEROS)"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.get_codigo()}{self.nome}"
    
    def clean(self):
        """Validação personalizada"""
        if self.nome:
            self.nome = self.nome.strip()
            
            # Validar tamanho mínimo
            if len(self.nome) < 2:
                raise ValidationError({'nome': 'Nome da categoria deve ter pelo menos 2 caracteres.'})
            
            # Verificar duplicatas (case-insensitive)
            if Categoria.objects.filter(nome__iexact=self.nome).exclude(pk=self.pk).exists():
                raise ValidationError({'nome': f'Já existe uma categoria com o nome "{self.nome}".'})
    
    def save(self, *args, **kwargs):
        """Sobrescrever save para limpar espaços"""
        if self.nome:
            self.nome = self.nome.strip()
        super().save(*args, **kwargs)
    
    def get_codigo(self):
        """Retorna o código formatado com 9 dígitos"""
        return str(self.id).zfill(9)
    
    def get_codigo_completo(self):
        """
        Retorna código + nome no formato de exportação FTP (111 caracteres)
        Formato: 9 dígitos (ID) + 102 caracteres (nome com espaços à direita)
        Exemplo: 000000001CASTANHAS                                                                                           
        """
        codigo = self.get_codigo()
        nome_formatado = self.nome.ljust(102)  # Preenche com espaços à direita até 102 caracteres
        return f"{codigo}{nome_formatado}"
    
    def get_total_produtos(self):
        """Retorna o total de produtos vinculados a esta categoria"""
        return self.produtos.count()
    
    def pode_deletar(self):
        """Verifica se a categoria pode ser deletada (sem produtos vinculados)"""
        return self.produtos.count() == 0

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
    
    nome = models.CharField(
        max_length=255,
        verbose_name="Nome do Produto",
        help_text="Nome completo do produto"
    )
    descricao = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descrição",
        help_text="Descrição detalhada do produto"
    )
    quantidade = models.IntegerField(
        default=0,
        verbose_name="Quantidade em Estoque",
        help_text="Quantidade disponível em estoque"
    )
    valor = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Valor (R$)",
        help_text="Preço de venda do produto"
    )
    imagem = models.ImageField(
        upload_to='produtos_imagens/', 
        blank=True, 
        null=True, 
        default='produtos_imagens/placeholder.png',
        verbose_name="Imagem do Produto"
    )
    ref = models.CharField(
        max_length=250, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Referência",
        help_text="Código de referência único do produto (gerado automaticamente)"
    )
    unidade_de_medida = models.CharField(
        max_length=2, 
        choices=UNIDADES_MEDIDA, 
        default='kg',
        verbose_name="Unidade de Medida"
    )
    valor_da_medida = models.DecimalField(
        max_digits=100, 
        decimal_places=2, 
        default=0,
        verbose_name="Valor da Medida",
        help_text="Valor da unidade de medida"
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='produtos',
        verbose_name="Categoria"
    )
    usuario_cadastro = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='produtos_cadastrados',
        verbose_name="Usuário que Cadastrou"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_alteracao = models.DateTimeField(auto_now=True, verbose_name="Última Alteração")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-data_criacao']

    def __str__(self):
        return self.nome
    
    def clean(self):
        """Validação personalizada"""
        if self.valor and self.valor < 0:
            raise ValidationError({'valor': 'O valor do produto não pode ser negativo.'})
        
        if self.valor_da_medida and self.valor_da_medida < 0:
            raise ValidationError({'valor_da_medida': 'O valor da medida não pode ser negativo.'})
    
    def save(self, *args, **kwargs):
        """Sobrescrever save para limpar dados"""
        if self.nome:
            self.nome = self.nome.strip()
        super().save(*args, **kwargs)
    
    def get_codigo_barras(self):
        """Retorna o código de barras formatado com 13 dígitos"""
        return str(self.id).zfill(13)
    
    def get_ref_completo(self):
        """
        Retorna a referência completa no formato de exportação FTP (217 caracteres)
        Formato: codigo_barras(13) + descricao(160) + unidade(4) + valor(10) + estoque(10) + valor_medida(10) + categoria(10)
        """
        codigo_barras = self.get_codigo_barras()
        descricao = self.nome[:160].ljust(160)  # Limita a 160 e preenche com espaços
        unidade = self.unidade_de_medida.ljust(4)
        valor_centavos = str(int(self.valor * 100)).zfill(10)
        estoque = str(self.quantidade).zfill(10)
        valor_medida_centavos = str(int(self.valor_da_medida * 100)).zfill(10)
        categoria_id = str(self.categoria.id).zfill(10) if self.categoria else '0000000000'
        
        return f"{codigo_barras}{descricao}{unidade}{valor_centavos}{estoque}{valor_medida_centavos}{categoria_id}"
    
    def esta_em_estoque(self):
        """Verifica se o produto está em estoque"""
        return self.quantidade > 0
    
    def get_valor_formatado(self):
        """Retorna o valor formatado em reais"""
        return f"R$ {self.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
