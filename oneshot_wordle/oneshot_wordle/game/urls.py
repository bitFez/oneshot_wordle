from django.urls import path

from oneshot_wordle.game.views import (
    wordle,
    load_words,
)

app_name = "game"
urlpatterns = [
    path("", wordle, name="home"),
    path("load_words", load_words, name="load_words"),
]
