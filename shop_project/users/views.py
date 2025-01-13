from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from .forms import CustomUserCreationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        print(request.POST)
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            print(f"User {username} successfully registered!")
            messages.success(request, f'Аккаунт {username} успешно создан! Теперь вы можете войти.')
            login(request, user)  # Авторизуем пользователя
            return redirect('index')

    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


