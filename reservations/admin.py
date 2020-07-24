from django.contrib import admin
from .models import WorkDay, Schedule, Reservation

admin.site.register(WorkDay)
admin.site.register(Schedule)
admin.site.register(Reservation)

