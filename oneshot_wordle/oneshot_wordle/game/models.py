from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Yetle(models.Model):
    word = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    correctAnswers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word

class Word(models.Model):
    word = models.CharField(max_length=5)
    
    def __str__(self):
        return self.word

class Wordle_Attempt(models.Model):
    word = models.ForeignKey(Yetle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)