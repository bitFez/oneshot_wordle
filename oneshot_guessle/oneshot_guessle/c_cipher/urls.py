from django.urls import path

from oneshot_guessle.c_cipher.views import (
    c_index, c_puzzle_view, c_puzzle_preview, c_about, c_preview_hijri_year
)

app_name = "c_cipher"
urlpatterns = [
    path('cc/', c_index, name='c_index'),  # Index view for the game
    path('cc/about', c_about, name='c_about'),
    path('cc/preview-hijri/<int:hijri_year>/', c_preview_hijri_year, name='preview_hijri_year'),  # Admin preview for hijri year template
    path('cc/<int:year>/day/<int:day>/', c_puzzle_view, name='puzzle_view'),
    # Dev preview/test path: bypasses release/prerequisite gating
    path('cc/preview/<slug:slug>/', c_puzzle_preview, name='puzzle_preview'),
]


