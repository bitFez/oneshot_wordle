from django.urls import path

from oneshot_guessle.tangle.views import (
    submit_words, tangle_index, tangleRankings
)

app_name = "tangle"
urlpatterns = [
    path('tangle', tangle_index, name='tangle_index'),  # Index view for the tangle game
    path('tangle/submit-words/', submit_words, name='submit_words'),    
    path('tangle/rankings/', tangleRankings, name='tangle_rankings'),    
    
    # Ads View
    # path('ads.txt', serve_ads_txt, name='ads.txt'),
]

