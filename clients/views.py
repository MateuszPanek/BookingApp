from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from BookingApp.settings import PLATFORM_NAME, PLATFORM_URL
from website.messages import send_email
from .forms import (ClientRegisterForm,
                    ClientCreateForm,
                    ClientUpdateForm,
                    ClientUpdateByStaffForm,
                    ClientProfileUpdateForm,
                    SendCredentialsForm)
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


class ClientList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ClientProfile
    context_object_name = 'objects'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ClientCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    @staticmethod
    def get(request):
        form = ClientCreateForm()
        form2 = ClientProfileUpdateForm()
        form3 = SendCredentialsForm()
        context = {
            'user_form': form,
            'profile_form': form2,
            'credentials_form': form3
        }
        return render(request, 'clients/client_create.html', context)

    @staticmethod
    def post(request):
        form = ClientCreateForm(request.POST)
        form2 = ClientProfileUpdateForm(request.POST)
        form3 = SendCredentialsForm(request.POST)

        if form.is_valid() and form2.is_valid():
            user = form.save()
            profile = form2.save(commit=False)
            profile.user = form.instance
            form2.save()
            if form3.is_valid():
                try:
                    if form3.cleaned_data['send_credentials'] is True:
                        details = {
                            'recipient': user.email,
                            'subject': f'Account was created for you at {PLATFORM_NAME}',
                            'message': f'Hello Dear {user.first_name}!\n Our staff member created you an account.'
                                       f'Please login to the system under : {PLATFORM_URL}\n'
                                       f'Your login credentials - please change your password after first login:'
                                       f'Username {user.username} password {user.password}'
                        }
                        send_email(details)
                except AttributeError:
                    pass
        return redirect('clients_list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ClientUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        form = ClientUpdateByStaffForm(instance=user)
        form2 = ClientProfileUpdateForm(instance=user.clientprofile)

        data = {
            'first_name': user.first_name,
            'email': user.email,
            'image': user.clientprofile.image.url,
            'id': user.id,
        }

        context = {
           'user_form': form,
           'profile_form': form2,
            'data': data
        }

        return render(request, 'clients/client_update.html', context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        form = ClientUpdateByStaffForm(request.POST, instance=user)
        form2 = ClientProfileUpdateForm(request.POST, request.FILES, instance=user.clientprofile)

        if form.is_valid() and form2.is_valid():
            form.save()
            form2.save()
            return redirect('clients_list')

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    success_url = '/client/list'
    template_name = 'personnel/user_confirm_delete.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False

