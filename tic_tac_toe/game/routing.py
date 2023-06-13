from django.urls import re_path

from . import player

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<room_name>\w+)/$", player.Player.as_asgi()),
]
