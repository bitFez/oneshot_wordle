from django.urls import path

from oneshot_wordle.game.views import (
    wordle,
)

app_name = "game"
urlpatterns = [
    path("", wordle, name="home"),
]
