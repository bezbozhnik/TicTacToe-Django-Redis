from django.db import models
class Game(models.Model):
    board = models.CharField(max_length=9)
    current_player = models.CharField(max_length=1)
    is_win = models.BooleanField(default=False)
    def check_win(self):
        board = self.board
        for i in range(0, 9, 3):
            if board[i] == board[i + 1] == board[i + 2] != ' ':
                return True
        for i in range(3):
            if board[i] == board[i + 3] == board[i + 6] != ' ':
                return True
        if board[0] == board[4] == board[8] != ' ':
            return True
        if board[2] == board[4] == board[6] != ' ':
            return True

        return False

