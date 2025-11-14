from django.contrib import admin
from .models import Produto, Categoria

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('get_codigo', 'nome', 'get_codigo_completo', 'data_criacao')
    search_fields = ('nome',)
    readonly_fields = ('data_criacao',)

class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'quantidade',
        'valor',
        'unidade_de_medida',
        'categoria',
        'ref',
        'usuario_cadastro',
        'data_criacao',
        'data_alteracao'
    )
    search_fields = ('nome', 'ref')
    list_filter = ('usuario_cadastro', 'categoria', 'unidade_de_medida', 'data_criacao')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario_cadastro = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Produto, ProdutoAdmin)


