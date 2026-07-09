from django.urls import path

from oneshot_guessle.bulls.views import (
    cb_index
)

app_name = "bulls"
urlpatterns = [
    path('bulls', cb_index, name='cb_index'),  # Index view for the cows and bulls game
]

