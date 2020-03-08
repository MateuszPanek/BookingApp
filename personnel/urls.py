from django.urls import path
from .views import PersonnelList, PersonnelUpdate, PersonnelCreate, PersonnelDelete

urlpatterns = [

    path('', PersonnelList.as_view(), name='personnel_list'),
    path('update/<int:pk>/', PersonnelUpdate.as_view(), name='personnel_update'),
    path('create/', PersonnelCreate.as_view(), name='personnel_create'),
    path('delete/<int:pk>/', PersonnelDelete.as_view(), name='personnel_delete'),

]
