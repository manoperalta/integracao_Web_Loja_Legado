from django.db import models

class LojaConfiguracao(models.Model):
    nome = models.CharField(max_length=255)
    cor_primaria = models.CharField(max_length=7, default='#FFFFFF')
    cor_secundaria = models.CharField(max_length=7, default='#000000')
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    ie = models.CharField(max_length=14, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Configuração da Loja"
        verbose_name_plural = "Configurações da Loja"

    def __str__(self):
        return self.nome

