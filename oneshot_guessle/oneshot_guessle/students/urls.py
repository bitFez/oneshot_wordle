from django.urls import path

from oneshot_guessle.students.views import (student, fakestudent)
# from oneshot_guessle.game.views import (AdsView)

app_name = "students"

urlpatterns = [
    path("student", student, name="student"),
    path('fake/', fakestudent, name='fake'),
    # path('ads.txt', AdsView.as_view()),
]
