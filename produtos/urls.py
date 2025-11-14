from django.urls import path
from . import views

urlpatterns = [
    # URLs para Categoria
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/criar/", views.criar_categoria, name="criar_categoria"),
    path("categorias/criar-ajax/", views.criar_categoria_ajax, name="criar_categoria_ajax"),
    path("categorias/editar/<int:pk>/", views.editar_categoria, name="editar_categoria"),
    path("categorias/deletar/<int:pk>/", views.deletar_categoria, name="deletar_categoria"),
    path("categorias/detalhes/<int:pk>/", views.detalhes_categoria, name="detalhes_categoria"),
]
