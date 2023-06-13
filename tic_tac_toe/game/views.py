import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import Game


def loginPage(request):
    if request.method == 'POST':
        if 'registration' in request.POST:
            return redirect('/registration/')
        username, password = request.POST.get('username'), request.POST.get('password')
        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'Не существует такого пользователя')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
    context = {}
    return render(request, 'game/login.html', context)


def index(request):
    if not request.user.is_authenticated:
        return redirect('login/')
    if request.method == 'POST':
        if 'logoutUser' in request.POST:
            logout(request)
            return redirect('login/')
        elif 'create_game' in request.POST:
            game_id = random.randint(1, 100000)
            Game.objects.create(pk=game_id)
            return redirect(f'/game/{game_id}/')

    return render(request, 'game/home.html')


def registrationPage(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            return redirect('/login/')
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
        else:
            messages.error(request, 'Ошибка во время регистрации')
    context = {
        'form': UserCreationForm()
    }
    return render(request, 'game/registration.html', context)


def play_game(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    game = Game.objects.get(pk=pk)
    return render(request, 'game/play_game.html', {'pk': pk, 'game': game})
