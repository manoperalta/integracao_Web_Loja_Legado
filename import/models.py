from django.db import models

class FTPConfig(models.Model):
    """
    Configuração centralizada do servidor FTP para importação de dados.
    Deve haver apenas uma configuração ativa no sistema.
    """
    nome = models.CharField(
        max_length=100, 
        default="Servidor FTP Principal",
        verbose_name="Nome da Configuração"
    )
    host = models.CharField(
        max_length=255, 
        verbose_name="Host FTP",
        help_text="Endereço do servidor FTP (ex: ftp.exemplo.com.br)"
    )
    porta = models.IntegerField(
        default=21,
        verbose_name="Porta",
        help_text="Porta do servidor FTP (padrão: 21)"
    )
    usuario = models.CharField(
        max_length=100, 
        verbose_name="Usuário",
        help_text="Nome de usuário para autenticação FTP"
    )
    senha = models.CharField(
        max_length=255, 
        verbose_name="Senha",
        help_text="Senha para autenticação FTP"
    )
    diretorio = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Diretório",
        help_text="Diretório/pasta no servidor FTP onde estão os arquivos (ex: 1)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Apenas uma configuração pode estar ativa por vez"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Configuração FTP"
        verbose_name_plural = "Configurações FTP"
        ordering = ['-ativo', '-data_atualizacao']
    
    def __str__(self):
        status = "✓ Ativo" if self.ativo else "✗ Inativo"
        return f"{self.nome} ({self.host}) - {status}"
    
    def save(self, *args, **kwargs):
        """
        Garante que apenas uma configuração esteja ativa por vez.
        """
        if self.ativo:
            # Desativa todas as outras configurações
            FTPConfig.objects.filter(ativo=True).update(ativo=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config_ativa(cls):
        """
        Retorna a configuração FTP ativa.
        """
        try:
            return cls.objects.filter(ativo=True).first()
        except cls.DoesNotExist:
            return None
