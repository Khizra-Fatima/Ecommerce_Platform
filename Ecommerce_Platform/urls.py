"""
URL configuration for Ecommerce_Platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),  # Main application URLs
    path('accounts/', include('accounts.urls')),  # Accounts-related URLs
    path('products/', include('products.urls')),  # Product-related URLs
    path('activities/', include('activities.urls')), # Activities-related URLs
    path('cart/', include('cart.urls')), # Cart-related URLs
    path('order/', include('orders.urls')), # Order-related URLs
    path('reviews/', include('reviews.urls')), # Review-related URLs
    path('chatbot/', include('chatbot.urls')),
    #path('payment/', include('payments.urls')), # Payment-related URLs
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



#handler404 = 'accounts.views.custom_404_view'
