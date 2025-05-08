from django.urls import path
from . import views
from .views import ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('all_products/', views.all_products, name='all_products'),
    path('create_product/', views.create_product, name='create_product'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/', ProductListCreateAPIView.as_view(), name='api-product-list'),
    path('product/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='api-product-detail'),
] 
