from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView

from BookingApp.settings import PLATFORM_NAME
from clients import forms as clients_forms
from personnel import forms as personnel_forms
from .forms import ContactForm
from .messages import send_email
from .models import Service


def home(request):
    context = {
        'services': Service.objects.all()
    }
    return render(request, 'website/home.html', context)


class ServicesList(ListView):
    model = Service
    template_name = 'website/services.html'
    context_object_name = 'services'


@login_required
def profile(request):
    return render(request, 'website/profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = clients_forms.ClientUpdateForm(request.POST, instance=request.user)

        if request.user.is_staff:
            profile_form = personnel_forms.PersonnelProfileUpdateForm(request.POST,
                                                                      request.FILES,
                                                                      instance=request.user.personnelprofile)

        elif not request.user.is_staff:
            profile_form = clients_forms.ClientProfileUpdateForm(request.POST,
                                                                 request.FILES,
                                                                 instance=request.user.clientprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'{request.user.first_name} your account was updated.')
            return redirect('profile')

    else:

        if request.user.is_staff:
            profile_form = personnel_forms.PersonnelProfileUpdateForm(instance=request.user.personnelprofile)

        elif not request.user.is_staff:
            profile_form = clients_forms.ClientProfileUpdateForm(instance=request.user.clientprofile)

        user_form = clients_forms.ClientUpdateForm(instance=request.user)
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }

        return render(request, 'website/edit_profile.html', context)


class ContactView(View):
    @staticmethod
    def get(request):
        form = ContactForm()
        context = {'form': form}
        return render(request, 'website/contact_form.html', context)

    def post(self, request):
        form = ContactForm(data=request.POST)
        if form.is_valid():
            if form.cleaned_data['contact_consent'] is True:
                messages.success(request, f'Message was sent. Thank you {form.cleaned_data["sender"]}!')
                data = {
                    'subject': form.cleaned_data['subject'],
                    'message': form.cleaned_data['message'],
                    'email': form.cleaned_data['email'],
                    'sender': form.cleaned_data['sender'],
                    'contact_consent': form.cleaned_data['contact_consent']
                }
                details = {
                    'subject': f'Your message was registered at {PLATFORM_NAME}.',
                    'message': f'Hello {data["sender"]}!\n'
                               f'Our team received your message:\n{data["message"]}\n '
                               f'We will contact you as soon as possible.\n'
                               f'Best regards\n'
                               f'{PLATFORM_NAME}',
                    'recipient': data['email']
                }
                send_email(details)
                form.save()
                return redirect('home')
            else:
                messages.warning(request, 'You need to give us your consent to be contacted.')
                form = ContactForm(data=request.POST)
                return render(request, 'website/contact_form.html', {'form': form})
        return render(request, 'website/contact_form.html', {'form': form})
