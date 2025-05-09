from django.urls import path
from . import views
from .views import (
    OrderListCreateAPIView,
    OrderRetrieveUpdateDestroyAPIView,
    SellerOrdersAPIView,
    ClearOrderHistoryAPIView,
)


urlpatterns = [
    path('checkout/<int:product_id>/', views.OrderCheckoutView.as_view(), name='order_checkout_page'),
    path('order-success/', views.OrderSuccessView, name='order_success'),
    path('order-history/', views.order_list_or_order_history, name='order_list'),
    path('all-order/', views.seller_orders, name='seller_orders'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('order-details/<int:order_id>', views.order_detail, name='order_details'),
    path('delete/<int:order_product_id>/', views.delete_order_history_product, name='delete_order_history_product'),
    path('clear_order-history/', views.clear_order_history, name='clear_order_history'),
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderRetrieveUpdateDestroyAPIView.as_view(), name='order-detail'),
    path('seller/orders/', SellerOrdersAPIView.as_view(), name='seller-orders'),
    path('orders/clear-history/', ClearOrderHistoryAPIView.as_view(), name='clear-order-history'),
]