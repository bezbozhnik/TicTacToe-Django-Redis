from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Game
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
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
            return redirect(f'/game/{request.user.id}/')
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
    game_id = request.session.get('game_id')
    if not request.user.is_authenticated:
        return redirect('login/')
    response_data = {}
    if game_id:
        game = Game.objects.get(pk=game_id)
    else:
        game = Game.objects.create(board=' ' * 9, current_player='X')
        request.session['game_id'] = pk

    board = game.board

    if request.method == 'POST':
        position = int(request.POST['position'])
        if board[position] == ' ':
            board = board[:position] + game.current_player + board[position+1:]
            if ' ' not in board or game.check_win():
                game.board = ' ' * 9
                game.save()
                response_data['winner'] = game.current_player if game.check_win() else None
            else:
                game.board = board
                game.current_player = 'O' if game.current_player == 'X' else 'X'
                game.save()
                response_data['winner'] = None

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        print(request.session['game_id'])
        response_data['board_html'] = render(request, 'game/play_game.html', {'board': game.board}).content.decode('utf-8')
        return JsonResponse(response_data)
    else:
        print(request.session['game_id'])
        return render(request, 'game/play_game.html', {'board': game.board})
