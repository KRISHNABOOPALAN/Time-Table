from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TimeTable, TimeSlot

class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['class_name', 'no_of_days', 'no_of_period', 'start_time', 'duration', 'no_of_breaks']

class BreakForm(forms.Form):
    break_number = forms.IntegerField(widget=forms.HiddenInput())
    after_period = forms.IntegerField(label='Break after the period of')
    duration = forms.IntegerField(label='Duration of this break (in mins)')

class AssignForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['subject', 'teacher']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user



class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)
