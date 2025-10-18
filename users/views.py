from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from users.forms import CustomUserCreationForm, CustomAuthenticationForm
from filmmate.settings import LOGIN_REDIRECT_URL

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(LOGIN_REDIRECT_URL)  # Change to your homepage
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(LOGIN_REDIRECT_URL)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@require_POST
def logout_view(request):
    logout(request)
    return redirect(LOGIN_REDIRECT_URL)
