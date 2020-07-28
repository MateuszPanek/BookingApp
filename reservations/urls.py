from django.urls import path

from . import views

urlpatterns = [
    path('workdays/', views.WorkDaysList.as_view(), name='workdays'),
    path('workdays/create', views.WorkDayCreate.as_view(), name='workday_create'),
    path('workdays/update/<int:pk>', views.WorkDayUpdate.as_view(), name='workday_update'),
    path('workdays/delete/<int:pk>', views.WorkDayDelete.as_view(), name='workday_delete'),
    path('monthly_schedule/', views.MonthlyScheduleList.as_view(), name='monthly_schedule'),
    path('monthly_schedule/<int:pk>', views.MonthlyScheduleList.as_view(), name='monthly_schedule'),
    path('monthly_schedule/create/', views.MonthlyScheduleCreate.as_view(), name='monthly_schedule_create'),
    path('monthly_schedule/create/<int:pk>', views.MonthlyScheduleCreate.as_view(), name='monthly_schedule_create'),
    path('monthly_schedule/delete/<int:pk>', views.MonthlyScheduleDelete.as_view(), name='monthly_schedule_delete'),
    path('daily_schedule/create/<int:pk>', views.DailyScheduleCreate.as_view(), name='daily_schedule_create'),
    path('daily_schedule/<int:pk>', views.DailyScheduleList.as_view(), name='daily_schedule'),
    path('schedule/import', views.ScheduleImport.as_view(), name='schedule_import'),
    path('schedule/<int:pk>', views.ScheduleView.as_view(), name='schedule'),
    path('schedule/create', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedule/update/<int:pk>', views.ScheduleUpdate.as_view(), name='schedule_update'),
    path('', views.ReservationList.as_view(), name='reservations'),
    path('update/<int:pk>', views.ReservationUpdate.as_view(), name='reservation_update'),
    path('create/', views.ReservationCreate.as_view(), name='reservation_create'),
    path('staff_reservation_create/', views.StaffReservationCreate.as_view(), name='staff_reservation_create'),
    path('delete/<int:pk>', views.ReservationDeleteView.as_view(), name='reservation_delete')


]

