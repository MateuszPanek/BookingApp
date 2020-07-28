from django.contrib import admin
from .models import WorkDay, Schedule, Reservation, MonthlySchedule, DailySchedule

admin.site.register(WorkDay)
admin.site.register(Schedule)
admin.site.register(Reservation)
admin.site.register(MonthlySchedule)
admin.site.register(DailySchedule)
