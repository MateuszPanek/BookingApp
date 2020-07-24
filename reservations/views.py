from reservations import availability_check
from reservations.availability_check import get_month_number
import datetime
from django.shortcuts import get_list_or_404, Http404
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import WorkDay, Schedule, Reservation, MonthlySchedule, DailySchedule
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms.widgets import CheckboxSelectMultiple, SelectDateWidget
from django.forms.models import modelform_factory
from .forms import ServiceSelection, PersonSelection, ReservationServiceSelection, ReservationPersonSelection,\
    ReservationCreate, ReservationDateSelection, ClientSelectionForm, ServiceSelectionForm, StaffReservationPersonSelection
import json
from website.models import Service
from personnel.models import PersonnelProfile, ClientProfile
from reservations.tools import date_form_generator, date_form_handler


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
        print(monthly_schedule.user_id)
        return f'/reservations/monthly_schedule/{monthly_schedule.user_id}'

    # def get(self, request, *args, **kwargs):
    #     print(self.request.GET)
    #     print(self.request)
    #     print(self.kwargs)
    #     return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        MonthlyScheduleDelete.success_url = self.success_url_getter(request, *args, **kwargs)
        print(self.request)
        print(self.kwargs)
        print(self.request.POST)
        return super().post(self, request, *args, **kwargs)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class DailyScheduleCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = DailySchedule
    success_url = 'reservations/daily_schedule'

    fields = 'day', 'start_time', 'end_time', 'break_start', 'break_end'
    widgets = {
        'day': SelectDateWidget,
    }

    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)

    def success_url_getter(self, request):
        return f'{self.request.POST["month"][0]}'

    def form_valid(self, form, request):
        self.object = form.save(commit=False)
        self.object['month'] = self.kwargs['ok']

        self.object.save()
        return HttpResponseRedirect(self.success_url_getter(request))

    def post(self, request, *args, **kwargs):
        DailyScheduleCreate.success_url = self.success_url_getter(request)
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


class ReservationList(LoginRequiredMixin, ListView):
    model = Reservation
    context_object_name = 'objects'
    paginate_by = 10
    ordering = ['-id']

    def get_queryset(self):
        if not self.request.user.is_staff:
            queryset = Reservation.objects.filter(client=self.request.user.clientprofile)
        elif self.request.user.is_staff and not self.request.user.is_superuser:
            queryset = Reservation.objects.filter(user=self.request.user.personnelprofile)
        elif self.request.user.is_superuser:
            return super().get_queryset()
        return queryset

    # def get_context_data(self, **kwargs):
    #     if not self.request.user.is_staff:
    #         reservations = Reservation.objects.filter(client=self.request.user.clientprofile)
    #     elif self.request.user.is_staff and not self.request.user.is_superuser:
    #         reservations = Reservation.objects.filter(user=self.request.user.personnelprofile)
    #     elif self.request.user.is_superuser:
    #         return super().get_context_data()
    #     return super().get_context_data(object_list=reservations)
    # # @TODO chekc why ordering is not working when data is filtered
    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #     return super().get(self, request, context=context, *args, **kwargs)


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

    def get(self, request):
        client_list = ClientProfile.objects.all()
        client_names = [client for client in client_list]
        form = ClientSelectionForm(client_names=client_names)
        return render(self.request, 'reservations/reservation_client_selection.html', context={'form': form})

    def post(self, request):
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
            service = Service.objects.get(id = self.request.POST['service'])
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
            client = ClientProfile.objects.get(user__first_name=client_name[0], user__last_name=' '.join(client_name[1:]))
            context = date_form_generator(self.request.POST, client)

            return render(request, 'reservations/reservation_date_selection.html', context)

        if 'date_selection' in self.request.POST:
            # client_name = self.request.POST['client'].split()
            client = ClientProfile.objects.get(id=self.request.POST['client'])
            if date_form_handler(self.request.POST, client):
                return redirect(StaffReservationCreate.success_url)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ReservationCreate(LoginRequiredMixin, UserPassesTestMixin, ModelFormWidgetMixin, CreateView):
    model = Reservation
    success_url = '/reservations'

    @staticmethod
    def get(request):
        form = ServiceSelection()
        return render(request, 'reservations/reservation_service_selection.html', context={'form': form})

    @staticmethod
    def post(request):

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
                """
                Selected service data should be saved for the 3rd stage
                """
                return render(request, 'reservations/reservation_person_selection.html', context)
            return HttpResponse('Service incorrect', 404)

        if 'person_selection' in request.POST:
            service = Service.objects.get(id=request.POST['service'])
            usr = request.POST['user'].split()
            client = request.user.clientprofile
            person = PersonnelProfile.objects.get(user__first_name=usr[0], user__last_name=usr[1])
            availability = availability_check.get_reservations_for_client(service, person, client)
            months = [month for month in availability.keys()]
            year_now = datetime.datetime.now().year
            years = json.dumps({
                months[0]: year_now,
                months[1]: year_now if months[0] != 'December' else year_now + 1
            })
            months.insert(0, 'Select a month')
            date_form = ReservationDateSelection(availability.keys(), years, data={
                'service': service,
                'user': person,
                'years': years
            })
            context = {
                'availability': json.dumps(availability_check.availability_time_to_string(availability)),
                'service': service,
                'person': person,
                'date_form': date_form,
            }

            return render(request, 'reservations/reservation_date_selection.html', context)

        if 'date_selection' in request.POST:
            years = json.loads(request.POST['years'])
            date_time = datetime.datetime(
                year=years[request.POST['month']],
                month=get_month_number(request.POST['month']),
                day=int(request.POST['day']),
                hour=int(request.POST['time'].split(':')[0]),
                minute=int(request.POST['time'].split(':')[1])
            )
            user = PersonnelProfile.objects.get(id=int(request.POST['user']))
            service = Service.objects.get(id=int(request.POST['service']))
            client = request.user.clientprofile
            confirmed = availability_check.check_if_any_collisions(
                int(request.POST['user']),
                int(request.POST['service']),
                date_time
            )
            if confirmed is False and type(confirmed) == bool:
                return HttpResponse(403, 'Sorry - you already have reservation by this time')

            elif type(confirmed) == dict:
                if False in confirmed.values():
                    return HttpResponse(403, 'Sorry - you already have reservation by this time!')

            reservation = Reservation.objects.create(
                user=user,
                service=service,
                client=client,
                date=date_time.date(),
                start_time=date_time.time()
            )

            return redirect(ReservationCreate.success_url)

    def test_func(self):
        if not self.request.user.is_staff:
            return True
        return False


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    success_url = '/reservations'

    def get(self, request, pk):
        reservation = Reservation.objects.get(id=pk)
        print(f'Reservation user.id : {reservation.user.user_id}'
              f'Reservation client.id :{reservation.client.user_id}'
              f'Request user.id : {request.user.id}')
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




