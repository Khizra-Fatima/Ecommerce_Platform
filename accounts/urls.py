from django.urls import path, include
from . import views


urlpatterns = [
    # Admin URLs
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/overview/', views.overview, name='overview'),
    path('admin/users/', views.manage_users, name='user_management'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/products/', views.manage_products, name='product_management'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin/orders/', views.manage_orders, name='order_management'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),


    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/store/<int:store_id>/', views.seller_store, name='seller_store'),
    path('seller/edit-store/<int:store_id>/', views.edit_store, name='edit_store'),


    # User URLs
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/<int:owner_id>/', views.user_profile, name='user_profile'),
    path('user/profile/edit/<int:owner_id>/', views.edit_profile, name='edit_profile'),
    path('user/support/', views.support, name='support'),
    path('user/account_settings/', views.account_settings, name='account_settings'),


    # Other URLs
    path('register/', views.register, name='register'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('data-deletion/', views.data_deletion, name='data_deletion'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
]