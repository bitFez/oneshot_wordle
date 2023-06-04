from django.urls import path

from oneshot_guessle.game.views import (
    guessle, load_words, supporter,shareto_modal,privacy_policy,terms_and_conditions,disclaimer,
    help_menu, results, history, halloffame, support_menu, guessle_easy, guessle_hard
)

app_name = "game"
urlpatterns = [
    path("", guessle, name="home"),
    path("easy", guessle_easy, name="easy"),
    path("hard", guessle_hard, name="hard"),
    path("supporterredirect", supporter, name="supporterredirect"),
    path("load_words", load_words, name="load_words"),
    #path('/',process_word, name='process_word'),
    path('help',help_menu, name='help'),
    path('support',support_menu, name='support'),
    path('shareto',shareto_modal, name='shareto'),
    path('results', results, name='results'),
    path('history', history, name='history'),
    path('halloffame', halloffame, name='hof'),
    path('privacy_policy', privacy_policy, name='privacy_policy'),
    path('terms', terms_and_conditions, name='tsandcs'),
    path('disclaimer', disclaimer, name='disclaimer'),
]
