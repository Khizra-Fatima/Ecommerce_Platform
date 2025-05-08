from django.urls import path
from . import views

urlpatterns = [
    path('leave_review/<int:order_id>/', views.leave_reviews, name='leave_review'),
    path('all-leaved-reviews/', views.all_reviews, name='all_reviews'),
    path('seller-reviews/', views.seller_reviews, name='seller_reviews'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

] 