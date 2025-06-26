from django.urls import path

from oneshot_guessle.cows_bulls.views import (
    cb_index
)

app_name = "cows_bulls"
urlpatterns = [
    path('cows_bulls', cb_index, name='cb_index'),  # Index view for the cows and bulls game
]

