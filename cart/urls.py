from django.urls import path
from . import views

urlpatterns = [
    path('add-in-cart/<int:product_id>/', views.add_cart_product, name='add_cart_product'),
    path('cart-products/', views.cart_products, name='cart_products'),
    path('delete/<int:cart_product_id>/', views.delete_cart_product, name='delete_cart_product'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),

]
