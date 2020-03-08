from .models import PersonnelProfile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.forms.widgets import CheckboxInput
from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from .forms import PersonnelUpdateForm, PersonnelProfileUpdateForm, PersonnelCreateForm, SendCredentialsForm
from website.messages import send_email
from BookingApp.settings import PLATFORM_NAME


class PersonnelList(LoginRequiredMixin, UserPassesTestMixin, ListView):

    model = PersonnelProfile
    context_object_name = 'objects'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class PersonnelCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    @staticmethod
    def get(request):
        form = PersonnelCreateForm()
        form2 = PersonnelProfileUpdateForm()
        form3 = SendCredentialsForm()
        context = {
            'user_form': form,
            'profile_form': form2,
            'credentials_form': form3
        }
        return render(request, 'personnel/personnel_create.html', context)

    @staticmethod
    def post(request):
        form = PersonnelCreateForm(request.POST)
        form2 = PersonnelProfileUpdateForm(request.POST)
        form3 = SendCredentialsForm(request.POST)

        if form.is_valid() and form2.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            form.save()
            profile = form2.save(commit=False)
            profile.user = form.instance
            form2.save()
            #TODO fix send credentials feature
            if form3.send_credentials is True:
                details = {
                    'recipient': user.email,
                    'subject': f'Account was created for you at {PLATFORM_NAME}',
                    'message': f'Hello Dear {user.first_name}!\n Please login to the system with:'
                               f'Username {user.username} password {user.password}'
                }
                send_email(details)

        return redirect('personnel_list')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class PersonnelUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        form = PersonnelUpdateForm(instance=user)
        form2 = PersonnelProfileUpdateForm(instance=user.personnelprofile)

        data = {
            'first_name': user.first_name,
            'email': user.email,
            'image': user.personnelprofile.image.url,
            'id': user.id,
        }

        context = {
           'user_form': form,
           'profile_form': form2,
            'data': data
        }

        return render(request, 'personnel/personnel_update.html', context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        form = PersonnelUpdateForm(request.POST, instance=user)
        form2 = PersonnelProfileUpdateForm(request.POST, request.FILES, instance=user.personnelprofile)

        if form.is_valid() and form2.is_valid():
            form.save()
            form2.save()
            return redirect('personnel_list')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class PersonnelDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    success_url = '/personnel'
    template_name = 'personnel/user_confirm_delete.html'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False
