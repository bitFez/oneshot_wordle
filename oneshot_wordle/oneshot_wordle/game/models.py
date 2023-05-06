from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class OneshotWord(models.Model):
    class Meta: 
        verbose_name = "Daily Word"
        verbose_name_plural = "Daily Words"

    word = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    correctAnswers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.word

class OneshotClues(models.Model):
    class Meta: 
        verbose_name = "Clue"
        verbose_name_plural = "Clues"
    
    clue1 = models.CharField(max_length=5)
    clue2 = models.CharField(max_length=5)
    clue3 = models.CharField(max_length=5)
    clue4 = models.CharField(max_length=5)
    clue5 = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date)

class Word(models.Model):
    class Meta: 
        verbose_name = "Word"
        verbose_name_plural = "Words"

    word = models.CharField(max_length=5)
    frequency = models.PositiveBigIntegerField(default=0)
    lastOccurance = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.word

class Wordle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Word Attempt"
        verbose_name_plural = "Word Attempts"
    word = models.ForeignKey(OneshotWord, on_delete=models.CASCADE)
    guess = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)