from django.http import JsonResponse
from django.shortcuts import render
from .models import Game

def play_game(request):
    game_id = request.session.get('game_id')
    response_data = {}
    if game_id:
        game = Game.objects.get(pk=game_id)
    else:
        game = Game.objects.create(board=' ' * 9, current_player='X')
        request.session['game_id'] = game.id

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
        response_data['board_html'] = render(request, 'game/play_game.html', {'board': game.board}).content.decode('utf-8')
        return JsonResponse(response_data)
    else:
        return render(request, 'game/play_game.html', {'board': game.board})
