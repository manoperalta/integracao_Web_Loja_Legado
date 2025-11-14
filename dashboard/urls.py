from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # CRUD Produtos
    path('produtos/', views.produtos_list, name='produtos_list'),
    path('produtos/criar/', views.produto_create, name='produto_create'),
    path('produtos/<int:pk>/editar/', views.produto_update, name='produto_update'),
    path('produtos/<int:pk>/deletar/', views.produto_delete, name='produto_delete'),
    
    # CRUD Categorias
    path('categorias/', include('produtos.urls')),
    
    # CRUD Pedidos
    path('pedidos/', views.pedidos_list, name='pedidos_list'),
    path('pedidos/<int:pk>/', views.pedido_detail, name='pedido_detail'),
    path('pedidos/<int:pk>/editar/', views.pedido_update, name='pedido_update'),
    path('pedidos/<int:pk>/deletar/', views.pedido_delete, name='pedido_delete'),
    path('pedidos/<int:pk>/toggle-status/', views.toggle_pedido_status, name='toggle_pedido_status'),
]
