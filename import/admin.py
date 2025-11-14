from django.contrib import admin
from .models import FTPConfig

@admin.register(FTPConfig)
class FTPConfigAdmin(admin.ModelAdmin):
    list_display = ('nome', 'host', 'porta', 'usuario', 'diretorio', 'ativo', 'data_atualizacao')
    list_filter = ('ativo', 'data_criacao')
    search_fields = ('nome', 'host', 'usuario')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ativo')
        }),
        ('Configurações do Servidor', {
            'fields': ('host', 'porta', 'usuario', 'senha', 'diretorio')
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Garante que ao ativar uma configuração, as outras sejam desativadas.
        """
        if obj.ativo:
            FTPConfig.objects.filter(ativo=True).exclude(pk=obj.pk).update(ativo=False)
        super().save_model(request, obj, form, change)
