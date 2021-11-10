from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=True, help_text="Phone number")
    first = forms.CharField(max_length=20, required=True, help_text="First name")
    last = forms.CharField(max_length=20, required=True, help_text="Last name")

    class Meta:
        model = User
        fields = [
            "first",
            "last",
            "phone",
            "email",
            "username",
            "password1",
            "password2",
        ]
