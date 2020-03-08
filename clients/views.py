from django.contrib import messages
from django.shortcuts import render, redirect

from BookingApp.settings import PLATFORM_NAME, PLATFORM_URL
from website.messages import send_email
from .forms import ClientRegisterForm
from .models import ClientProfile
from .tokens import create_token


def register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            messages.success(request, f'Hello {first_name}. You have registered successfully.'
                                      f'Please click the link in confirmation e-mail to activate your account')
            client = form.save(commit=False)
            client.is_active = False
            form.save()
            token = create_token()
            ClientProfile.objects.create(user=form.instance, registration_token=token)
            # token = client.clientprofile.registration_token

            details = {

                'subject': f'Confirm your registration at {PLATFORM_NAME}',
                'message': f'Click the link in order to confirm your registration\n'
                           f'{PLATFORM_URL}client/registration_confirm/{token}',
                'recipient': f'{client.email}'

            }
            send_email(details)
            return redirect('login')
    else:
        form = ClientRegisterForm()
    return render(request, 'clients/register.html', {'form': form})


def confirm_registration(request, token):
    if request.method == 'GET':
        try:
            client = ClientProfile.objects.get(registration_token=token)
            client.confirmed_token = client.registration_token
            client.registration_token = None
            user = client.user
            user.is_active = True
            client.save()
            user.save()
            messages.success(request, f'Hello {client.user.username}. Your account has been activated successfully.'
                                      f'You are now able to login to your account')
            return redirect('login')
        except ClientProfile.DoesNotExist:
            try:
                client = ClientProfile.objects.get(confirmed_token=token)
                messages.success(request, f'Hello {client.user.username}. Your account has been already activated '
                                          f'In case of additional questions please use our contact form')
                return redirect('login')

            except ClientProfile.DoesNotExist:
                messages.warning(request, f'Hello! Looks like something went wrong. Please register again')

                return redirect('register')
