"""BookingApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from clients import views as clients_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    # path('register/', include('clients.urls')),
    path('client/', include('clients.urls')),
    path('register/', clients_views.register, name='register'),
    # path('profile/', website_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='website/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='website/logout.html'), name='logout'),

]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
