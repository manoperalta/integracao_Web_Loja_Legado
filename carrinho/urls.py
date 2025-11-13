from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("carrinho/", views.carrinho, name="carrinho"),
    path("checkout/", views.checkout, name="checkout"),
    
    path("get_cart_count/", views.get_cart_count, name="get_cart_count"),
    path("fechar_pedido/", views.fechar_pedido, name="fechar_pedido"),
    path("process_order/", views.processOrder, name="process_order"),
    path('atualizar_item/', views.atualizar_item, name='atualizar_item'),

]

