from django.urls import path

from oneshot_guessle.c_cipher.views import (
    c_index, c_puzzle_view, c_puzzle_preview
)

app_name = "c_cipher"
urlpatterns = [
    path('cc/', c_index, name='c_index'),  # Index view for the game
    path('cc/<int:year>/day/<int:day>/', c_puzzle_view, name='puzzle_view'),
    # Dev preview/test path: bypasses release/prerequisite gating
    path('cc/preview/<slug:slug>/', c_puzzle_preview, name='puzzle_preview'),
]

