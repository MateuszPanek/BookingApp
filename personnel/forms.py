from django import forms
from django.contrib.auth.models import User

from .models import PersonnelProfile


class PersonnelUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class PersonnelProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PersonnelProfile
        fields = ['birth_date', 'address', 'image']
