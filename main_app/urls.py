from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Explore-Products/', views.explore_area, name='buynow'),
    path('load-more-products/', views.load_more_products, name='load_more_products'),
]