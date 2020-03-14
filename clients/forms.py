from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ClientProfile


class ClientRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class ClientCreateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput()
        }


class ClientUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ClientUpdateByStaffForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']


class ClientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['birth_date', 'address', 'image']


class SendCredentialsForm(forms.Form):
    send_credentials = forms.BooleanField(required=False, label='Send credentials to specified e-mail')