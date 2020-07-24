from django import forms
from .models import Reservation, MonthlySchedule, DailySchedule
from website.models import Service
from personnel.models import PersonnelProfile, ClientProfile
from django.contrib.auth.models import User


class DailyScheduleCreate(forms.ModelForm):
    class Meta:
        model = DailySchedule
        fields = (
                'month', 'day',
                'start_time', 'end_time',
                'break_start', 'break_end'
                  )
        widgets = {
            'day': forms.SelectDateWidget
        }


class ServiceSelection(forms.ModelForm):
    select_service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(),
        empty_label='Please select a service',
        to_field_name='price'


    )

    class Meta:
        model = Service
        fields = ('select_service',)


class PersonSelection(forms.Form):

    def __init__(self, personnel_names, *args, **kwargs):
        super(PersonSelection, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(
            choices=tuple([(name, name) for name in personnel_names]),
            label='Select a person'
        )

    # class Meta:
    #     model = PersonnelProfile
    #     fields = 'user',
# class PersonSelection(forms.ModelForm):
#
#     def __init__(self, personnel_names, *args, **kwargs):
#         super(PersonSelection, self).__init__(*args, **kwargs)
#         self.fields['user'] = forms.ChoiceField(
#             choices=tuple([(name, name) for name in personnel_names]),
#             label='Select a person'
#         )
#
#     class Meta:
#         model = PersonnelProfile
#         fields = 'user',


class ReservationServiceSelection(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = 'service',


class ReservationPersonSelection(forms.ModelForm):
    def __init__(self, personnel_names, *args, **kwargs):
        super(ReservationPersonSelection, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(
            choices=tuple([(name, name) for name in personnel_names]),
            label='Select a person'
        )

    class Meta:
        model = Reservation
        fields = 'service', 'user'
        widgets = {
            'service': forms.HiddenInput()
        }


class ReservationDateSelection(forms.ModelForm):
    month = forms.ChoiceField()
    years = forms.ChoiceField()
    day = forms.ChoiceField(choices=[], required=False)
    time = forms.ChoiceField(choices=[], required=False)

    def __init__(self, months, years, *args, **kwargs):
        super(ReservationDateSelection, self).__init__(*args, **kwargs)
        self.fields['month'] = forms.ChoiceField(
            choices=tuple([(month, month) for month in months]),
            required=False
        )
        self.fields['years'] = forms.ChoiceField(
            choices=[(years, years)],
            required=False,
            widget=forms.HiddenInput(),
        )

    class Meta:
        model = Reservation
        fields = 'client', 'service', 'user', 'month', 'day', 'time', 'years' #added client for staff reservation
        widgets = {
            'client': forms.HiddenInput(), #check if it doesn't break client reservations
            'service': forms.HiddenInput(),
            'user': forms.HiddenInput(),
            # 'years': forms.HiddenInput()
        }


class ReservationCreate(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = 'service', 'user', 'date', 'start_time'


class ClientSelectionForm(forms.ModelForm):
    def __init__(self, client_names, *args, **kwargs):
        super(ClientSelectionForm, self).__init__(*args, **kwargs)
        self.fields['client'] = forms.ChoiceField(
            choices=tuple([(name, name) for name in client_names]),
            label='Select a client'
        )

    class Meta:
        model = Reservation
        fields = 'client',
        # widgets = {
        #     'service': forms.HiddenInput()
        # }
        #


class ServiceSelectionForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = 'client', 'service'
        widgets = {
            'client': forms.HiddenInput()
        }


class StaffReservationPersonSelection(ReservationPersonSelection):
    class Meta:
        model = Reservation
        fields = 'client', 'service', 'user'
        widgets = {
            'client': forms.HiddenInput(),
            'service': forms.HiddenInput()
        }
