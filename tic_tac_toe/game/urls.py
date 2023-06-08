from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('game/<int:pk>/', views.play_game, name='play_game'),
    path('login/', views.loginPage, name='login'),
    path('registration/', views.registrationPage, name='registration'),
]