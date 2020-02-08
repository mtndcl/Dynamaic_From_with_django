from django import forms
from .models import User, Profile, Project, Rolls
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(RegisterForm, self).__init__(*args, **kwargs)

    def clean_first_name(self, *args, **kwargs):
        first_name = self.cleaned_data.get('first_name')

        print('ValidationError   func worked')
        if len(first_name) < 3:
            raise forms.ValidationError("At least 4 character need")
        else:
            return first_name

    def clean_last_name(self, *args, **kwargs):
        last_name = self.cleaned_data.get('last_name')

        print('ValidationError   func worked')
        if len(last_name) < 3:
            raise forms.ValidationError("At least 4 character need")
        else:
            return last_name

    def clean_email(self, *args, **kwargs):
        email = self.cleaned_data.get('email')

        try:
            selected_user = User.objects.get(email=email)
            raise forms.ValidationError("this email Already have a account")
        except User.DoesNotExist:
            return email

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        username = self.cleaned_data.get('email')
        obj = super(RegisterForm, self).save(*args, **kwargs)
        if self.request:
            obj.user = self.request.user
        obj.username = username
        obj.is_active = False
        obj.save()
        return obj


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['organization', 'phone_number']


class UpdatePasswordForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'abstract']

    def save(self, *args, **kwargs):
        kwargs['commit'] = False

        obj = super(ProjectForm, self).save(*args, **kwargs)

        print("innnnnnnnnnn formmmmmmmmmm")
        obj.save()
        return obj

