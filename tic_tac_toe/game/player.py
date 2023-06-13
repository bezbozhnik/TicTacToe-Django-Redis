import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Game


class Player(AsyncWebsocketConsumer):
    connected_clients = {}

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.has_changed = False
        self.room_group_name = "chat_%s" % self.room_name
        if self.room_name not in self.connected_clients:
            self.connected_clients[self.room_name] = [self]
            self.move = 'X'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        elif len(self.connected_clients[self.room_name]) == 1:
            self.connected_clients[self.room_name].append(self)
            self.move = 'O'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("game_group", self.channel_name)
        await self.delete_game_board()

    @database_sync_to_async
    def update_game_board(self, position):
        game = Game.objects.get(pk=self.room_name)
        game.board = game.board[:position] + self.move + game.board[position + 1:]
        if ' ' not in game.board or game.check_win():
            game.board = ' ' * 9
        game.save()
        return game.board

    @database_sync_to_async
    def what_move(self):
        game = Game.objects.get(pk=self.room_name)
        return game.current

    @database_sync_to_async
    def change_move(self):
        if self.has_changed:
            self.has_changed = False
            game = Game.objects.get(pk=self.room_name)
            if game.current == 'X':
                game.current = 'O'
            else:
                game.current = 'X'
            game.save()

    @database_sync_to_async
    def delete_game_board(self):
        if self.room_name in self.connected_clients:
            self.connected_clients[self.room_name].remove(self)
            if len(self.connected_clients[self.room_name]) <= 0:
                del self.connected_clients[self.room_name]
                Game.objects.get(pk=self.room_name).delete()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        position = text_data_json['position']
        if self.move == await self.what_move():
            self.has_changed = True
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_position',
                    'board': await self.update_game_board(position)
                }
            )

    async def send_position(self, event):
        board = event['board']
        response = {
            'board': board
        }
        await self.change_move()
        await self.send(text_data=json.dumps(response))
