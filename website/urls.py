from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.ServicesList.as_view(), name='services'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('contact/', views.ContactView.as_view(), name='contact'),

]
