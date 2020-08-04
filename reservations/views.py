import datetime
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import WorkDay, Schedule, Reservation, MonthlySchedule, DailySchedule
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView, FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.widgets import CheckboxSelectMultiple, SelectDateWidget
from django.forms.models import modelform_factory
from django.contrib.auth.models import User
from .forms import DailyScheduleCreateForm, ServiceSelection, ReservationPersonSelection, \
    ClientSelectionForm, ServiceSelectionForm, \
    StaffReservationPersonSelection, ScheduleImportForm
from website.models import Service
from personnel.models import PersonnelProfile, ClientProfile
from reservations.tools import date_form_generator, date_form_handler, get_day_choices, is_day_in_schedule,\
    schedule_import_handler


class ModelFormWidgetMixin(object):
    def get_form_class(self):
        return modelform_factory(self.model, fields=self.fields, widgets=self.widgets)


class WorkDaysList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = WorkDay
    context_object_name = 'objects'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class WorkDayCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = WorkDay
    success_url = '/reservations/workdays'
    fields = ('name',)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class WorkDayUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = WorkDay
    success_url = '/reservations/workdays'
    fields = ('name',)
    template_name = 'reservations/worday_update.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class WorkDayDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = WorkDay
    success_url = '/reservations/workdays'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class ScheduleView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Schedule
    context_object_name = 'objects'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ScheduleCreateView(LoginRequiredMixin, UserPassesTestMixin, ModelFormWidgetMixin, CreateView):
    model = Schedule
    success_url = '/personnel'
    fields = ['user', 'availability_days', 'start_hour', 'end_hour']
    widgets = {
        'availability_days': CheckboxSelectMultiple,
    }

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class ScheduleUpdate(LoginRequiredMixin, UserPassesTestMixin, ModelFormWidgetMixin, UpdateView):
    model = Schedule
    success_url = '/personnel'
    fields = ['availability_days', 'start_hour', 'end_hour']
    widgets = {
        'availability_days': CheckboxSelectMultiple,
    }

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class MonthlyScheduleList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MonthlySchedule
    context_object_name = 'objects'

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            queryset = self.get_queryset().filter(user=self.kwargs['pk'])
            context = {
                'path': 'monthly_schedule',
                'objects': queryset,
                'user_id': self.kwargs['pk']
            }
            return render(request, 'reservations/monthlyschedule_list.html', context=context)
        else:
            queryset = self.get_queryset().filter()
            context = {
                'path': 'monthly_schedule',
                'objects': queryset,
            }
            return render(request, 'reservations/monthlyschedule_list.html', context=context)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        elif self.request.user.is_staff:
            return MonthlySchedule.objects.filter(user=self.request.user.personnelprofile)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class MonthlyScheduleCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MonthlySchedule
    success_url = '/reservations/monthly_schedule'
    fields = 'user', 'year', 'month'

    def success_url_getter(self, request, *args, **kwargs):
        return f'/reservations/monthly_schedule/{self.kwargs["pk"]}'

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            self.fields = 'year', 'month'
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        if pk:
            query_copy = self.request.POST.copy()
            query_copy['user'] = PersonnelProfile.objects.get(id=pk)
            self.request.POST = query_copy
            MonthlyScheduleCreate.success_url = self.success_url_getter(request, *args, **kwargs)
        user = self.request.POST['user']
        year = self.request.POST['year']
        month = self.request.POST['month']
        existing = MonthlySchedule.objects.filter(
            user=user,
            year=year,
            month=month
        )
        if existing:
            messages.add_message(self.request, messages.WARNING,
                                 'Schedule for this month already exists!',)
            return redirect('monthly_schedule')
        return super().post(self, request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class MonthlyScheduleDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MonthlySchedule
    success_url = '/reservations/monthly_schedule'

    def success_url_getter(self, request, *args, **kwargs):
        monthly_schedule = MonthlySchedule.objects.get(id=self.kwargs['pk'])
        return f'/reservations/monthly_schedule/{monthly_schedule.user_id}'

    def post(self, request, *args, **kwargs):
        MonthlyScheduleDelete.success_url = self.success_url_getter(request, *args, **kwargs)
        return super().post(self, request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class DailyScheduleCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = DailySchedule
    success_url = 'reservations/monthly_schedule'
    form = DailyScheduleCreateForm
    fields = 'month', 'day', 'start_time', 'end_time', 'break_start', 'break_end'

    def get(self, request, *args, **kwargs):
        form = DailyScheduleCreateForm(get_day_choices(self.kwargs['pk'], True))
        return render(request, 'reservations/dailyschedule_form.html', context={'form': form})

    def success_url_getter(self, request):
        return f'{self.kwargs.get("pk")}'

    def form_valid(self, form):
        wrong_form = False
        month = MonthlySchedule.objects.get(id=self.kwargs['pk'])
        breaks = [self.request.POST['break_start'], self.request.POST['break_end']]
        none_breaks = breaks.count('')
        if is_day_in_schedule(month, self.request.POST['day']):
            wrong_form = True
            messages.add_message(self.request, messages.WARNING,
                                 'Schedule for this day already exists! Please select another one', )
        if none_breaks == 1:
            wrong_form = True
            messages.add_message(self.request, messages.WARNING,
                                 'Please specify both break start and end time', )
        if none_breaks == 0:
            bs, be = datetime.datetime.strptime(breaks[0], '%H:%M'), datetime.datetime.strptime(breaks[1], '%H:%M')
            if bs > be:
                wrong_form = True
                messages.add_message(self.request, messages.WARNING,
                                     'Please make sure that break end time is greater than start time',)
        if wrong_form:
            form = DailyScheduleCreateForm(get_day_choices(self.kwargs['pk'], True))
            return render(self.request, 'reservations/dailyschedule_form.html', context={'form': form})
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        query_copy = self.request.POST.copy()
        month = MonthlySchedule.objects.get(id=self.kwargs.get('pk'))
        query_copy['month'] = month
        query_copy['day'] = datetime.date(int(month.year), int(month.month), int(query_copy['day'].split(' ')[0]))
        self.request.POST = query_copy
        DailyScheduleCreate.success_url = f'/reservations/daily_schedule/{self.success_url_getter(request)}'
        return super().post(self, request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class DailyScheduleList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DailySchedule
    context_object_name = 'objects'
    template_name = 'reservations/dailyschedule_list.html'

    def get(self, request, *args, **kwargs):
        schedule = DailySchedule.objects.filter(month=self.kwargs['pk'])
        if schedule.count() == 0:
            return HttpResponseRedirect(f'create/{self.kwargs["pk"]}')
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        return super(DailyScheduleList, self).get_queryset().filter(month=self.kwargs['pk'])

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ScheduleImportSingleUser(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = ScheduleImportForm
    template_name = 'reservations/file_upload.html'
    success_url = 'reservations/monthly_schedule'

    def get(self, request, *args, **kwargs):
        personnel_profiles = [person for person in PersonnelProfile.objects.all()]
        personnel_profiles.insert(0, 'General Update')
        form = ScheduleImportForm(personnel_profiles=personnel_profiles)
        return render(request, 'reservations/file_upload.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        personnel_profiles = [person for person in PersonnelProfile.objects.all()]
        personnel_profiles.insert(0, 'General Update')
        is_user = self.request.POST.get('user')
        if is_user != 'General Update':
            usr = self.request.POST['user'].split(' ')
            user = User.objects.get(first_name=usr[0], last_name=usr[1]).personnelprofile
            user_column = False
        else:
            user = None
            user_column = True
        update = True if self.request.POST.get('update_existing_days') == 'on' else False
        outcome = schedule_import_handler(self.request.FILES['file'], user, update, user_column)
        form = ScheduleImportForm(personnel_profiles=personnel_profiles)
        return render(request, 'reservations/file_upload.html', context={'form': form, 'outcome': outcome})

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ReservationList(LoginRequiredMixin, ListView):
    model = Reservation
    context_object_name = 'objects'
    paginate_by = 10
    ordering = ['-date']

    def get_queryset(self):
        if not self.request.user.is_staff:
            queryset = Reservation.objects.filter(client=self.request.user.clientprofile).order_by('-date')
        elif self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = Reservation.objects.filter(user=self.request.user.personnelprofile).order_by('-date')
        else:
            return super().get_queryset()
        return queryset


class ReservationUpdate(LoginRequiredMixin, UserPassesTestMixin, ModelFormWidgetMixin, UpdateView):
    model = Reservation
    success_url = '/reservations'
    fields = '__all__'
    widgets = {
        'date': SelectDateWidget
    }

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class StaffReservationCreate(LoginRequiredMixin, UserPassesTestMixin, ModelFormWidgetMixin, CreateView):
    model = Reservation
    success_url = '/reservations'

    def get(self, request, *args, **kwargs):
        client_list = ClientProfile.objects.all()
        client_names = [client for client in client_list]
        form = ClientSelectionForm(client_names=client_names)
        return render(self.request, 'reservations/reservation_client_selection.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        if 'client_selection' in self.request.POST:
            client = self.request.POST['client']
            service_form = ServiceSelectionForm()
            service_form.initial['client'] = client
            context = {
                'client': client,
                'service_form': service_form
            }

            return render(request, 'reservations/staff_reservation_service_selection.html', context)

        if 'service_selection' in self.request.POST:
            service = Service.objects.get(id=self.request.POST['service'])
            client = self.request.POST['client']
            available_personnel = PersonnelProfile.objects.filter(services=service)
            personnel_names = [prs for prs in available_personnel]
            person_form = StaffReservationPersonSelection(personnel_names=personnel_names)
            person_form.initial['service'] = service
            person_form.initial['client'] = client
            context = {
                'client': client,
                'service': service,
                'person_form': person_form
            }

            return render(request, 'reservations/reservation_person_selection.html', context)

        if 'person_selection' in self.request.POST:
            client_name = self.request.POST['client'].split()
            client = ClientProfile.objects.get(user__first_name=client_name[0],
                                               user__last_name=' '.join(client_name[1:]))
            context = date_form_generator(self.request.POST, client)
            return render(request, 'reservations/reservation_date_selection.html', context)

        if 'date_selection' in self.request.POST:
            client = ClientProfile.objects.get(id=self.request.POST['client'])
            if date_form_handler(self.request.POST, client):
                return redirect(StaffReservationCreate.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ReservationCreateView(LoginRequiredMixin, UserPassesTestMixin, ModelFormWidgetMixin, CreateView):
    model = Reservation
    success_url = '/reservations'

    def get(self, request, *args, **kwargs):
        form = ServiceSelection()
        return render(request, 'reservations/reservation_service_selection.html', context={'form': form})

    def post(self, request, *args, **kwargs):
        if 'service_selection' in request.POST:
            service_form = ServiceSelection(request.POST)
            if service_form.is_valid():
                service = service_form.cleaned_data['select_service']
                available_personnel = PersonnelProfile.objects.filter(services=service)
                personnel_names = [prs for prs in available_personnel]
                person_form = ReservationPersonSelection(personnel_names=personnel_names)
                person_form.initial['service'] = service
                context = {
                    'service': service,
                    'person_form': person_form
                }
                return render(request, 'reservations/reservation_person_selection.html', context)
            return HttpResponse('Service incorrect', 404)

        if 'person_selection' in request.POST:
            context = date_form_generator(request.POST, request.user.clientprofile)
            return render(request, 'reservations/reservation_date_selection.html', context)

        if 'date_selection' in request.POST:
            if date_form_handler(request.POST, request.user.clientprofile):
                return redirect(ReservationCreateView.success_url)

    def test_func(self):
        if not self.request.user.is_staff:
            return True
        return False


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    success_url = '/reservations'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        reservation = Reservation.objects.get(id=pk)
        if not self.request.user.is_staff:
            if reservation.client.user_id == self.request.user.id:
                return super().get(self, request, pk)
            else:
                return HttpResponseForbidden()
        elif self.request.user.is_staff and not self.request.user.is_superuser:
            if reservation.user.user_id == self.request.user.id:
                return super().get(self, request, pk)
            else:
                return HttpResponseForbidden()
        else:
            return super().get(self, request, pk)
