from django.db import models
import calendar
import datetime
from clients.models import ClientProfile
from personnel.models import PersonnelProfile
from website.models import Service


class WorkDay(models.Model):
    day_choices = [(str(i), calendar.day_name[i]) for i in range(7)]
    name = models.CharField(max_length=9, choices=day_choices, default='1', unique=True)

    def __str__(self):
        return self.get_name_display()


class Schedule(models.Model):
    user = models.OneToOneField(PersonnelProfile, on_delete=models.CASCADE)
    availability_days = models.ManyToManyField(WorkDay)
    start_hour = models.TimeField()
    end_hour = models.TimeField()

    def __str__(self):
        return f'Schedule of {self.user.user.first_name} {self.user.user.last_name}'


class MonthlySchedule(models.Model):
    user = models.ForeignKey(PersonnelProfile, on_delete=models.CASCADE)
    year_choices = [(str(datetime.date.today().year), datetime.date.today().year),
                    (str(datetime.date.today().year + 1), datetime.date.today().year + 1)]
    month_choices = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    year = models.CharField(max_length=4, choices=year_choices, default='1')
    month = models.CharField(max_length=9, choices=month_choices, default='1')

    def get_month_name(self):
        return calendar.month_name[int(self.month)]

    def __str__(self):
        return f'{calendar.month_name[int(self.month)]} {self.year}'


class DailySchedule(models.Model):
    month = models.ForeignKey(MonthlySchedule, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField(blank=True, null=True)
    break_end = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.day.day}/{self.month.month}/{self.month.year}'


class Reservation(models.Model):
    user = models.ForeignKey(PersonnelProfile, on_delete=models.PROTECT)
    client = models.ForeignKey(ClientProfile, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    date = models.DateField(blank=True)
    start_time = models.TimeField(blank=True)

    def __str__(self):
        return f'Reservation Date: {self.date} - {self.start_time}\n' \
               f'Personnel: {self.user.user.first_name} {self.user.user.last_name} ' \
               f'Client: {self.client.user.first_name} {self.client.user.last_name}'
