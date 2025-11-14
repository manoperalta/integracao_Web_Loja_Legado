from django.urls import path
from . import views

app_name = 'import'

urlpatterns = [
    path('', views.wizard_inicio, name='wizard_inicio'),
    path('categorias/', views.importar_categorias_ftp, name='importar_categorias'),
    path('produtos/', views.wizard_produtos, name='wizard_produtos'),
    path('produtos/importar/', views.importar_produtos_ftp, name='importar_produtos'),
]
