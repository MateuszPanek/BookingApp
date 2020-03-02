from django.urls import path

from . import views

urlpatterns = [

    path('registration_confirm/<token>/', views.confirm_registration, name='registration_confirm'),

]
