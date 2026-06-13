from django.urls import path

from oneshot_guessle.wordmorph.views import (
    morph_index
)

app_name = "wordmorph"
urlpatterns = [
    path('morph', morph_index, name='morph_index'),  # Index view for the tangle game
    # path('tangle/submit-words/', submit_words, name='submit_words'),    
    # path('tangle/rankings/', tangleRankings, name='tangle_rankings'),    
    
    # Ads View
    # path('ads.txt', serve_ads_txt, name='ads.txt'),
]

