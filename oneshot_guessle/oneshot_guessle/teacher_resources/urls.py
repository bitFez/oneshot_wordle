from django.urls import path

from oneshot_guessle.teacher_resources.views import (resources_page)
# from oneshot_guessle.game.views import (AdsView)

app_name = "teacher_resources"

urlpatterns = [
    path("resources_page/", resources_page, name="res_page"),
]
