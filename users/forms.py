from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password")
