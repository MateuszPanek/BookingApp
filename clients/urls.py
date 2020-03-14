from django.urls import path

from . import views

urlpatterns = [

    path('registration_confirm/<token>/', views.confirm_registration, name='registration_confirm'),
    path('list/', views.ClientList.as_view(), name='clients_list'),
    path('create/', views.ClientCreate.as_view(), name='client_create'),
    path('update/<int:pk>', views.ClientUpdate.as_view(), name='client_update'),
    path('delete/<int:pk>', views.ClientDeleteView.as_view(), name='client_delete')

]
