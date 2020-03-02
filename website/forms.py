from django import forms

from BookingApp.settings import PLATFORM_NAME
from .models import ContactFormMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactFormMessage
        fields = ['subject', 'message', 'sender', 'email', 'contact_consent']
        widgets = {
            'contact_consent': forms.CheckboxInput()
        }
        labels = {
            'contact_consent': f'I consent to be contacted by {PLATFORM_NAME}'
        }
