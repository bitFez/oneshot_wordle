from django.urls import path

from oneshot_wordle.game.views import (
    wordle,
    load_words,
    help_menu, results
)

app_name = "game"
urlpatterns = [
    path("", wordle, name="home"),
    path("load_words", load_words, name="load_words"),
    #path('/',process_word, name='process_word'),
    path('help',help_menu, name='help'),
    path('results', results, name='results'),
]
