from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/<int:product_id>/', views.wishlist_product, name='wishlist_product'),
    path('wishlisted-products/', views.wishlisted_product, name='wishlisted_product'),
    path('delete-wishlist-item/<int:wishlist_id>/', views.delete_wishlist_item, name='delete_wishlist_item'),
    path('clear_wishlist/', views.clear_wishlist, name='clear_wishlist'),
    path('your-notifications/', views.notification, name='notifications'),
    path("mark-as-read/<int:notification_id>/", views.mark_notification_as_read, name="mark_notification_as_read"),
    path("notification-count/", views.get_notification_count, name="get_notification_count"),
    path('delete/<int:notification_id>/', views.delete_list_notification, name='delete_list_notification'),
    path('clear_notification_list/', views.clear_notification_list, name='clear_notification_list'),
    path('inbox/', views.msginbox, name='inbox'),
    path('converstion/<int:user_id>/', views.msgchatformat, name='chatformat'),
    path('message/<int:user_id>/', views.msginput, name='message'),
]
