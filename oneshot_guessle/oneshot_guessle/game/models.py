from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
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

class OneshotCluesEasy(models.Model):
    class Meta: 
        verbose_name = "Easy Clue"
        verbose_name_plural = "Easy Clues"
    clue1 = models.CharField(max_length=5)
    clue2 = models.CharField(max_length=5)
    clue3 = models.CharField(max_length=5)
    clue4 = models.CharField(max_length=5)
    clue5 = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date)

class OneshotWord(models.Model):
    class Meta: 
        verbose_name = "Oneshot Daily Word"
        verbose_name_plural = "Oneshot Daily Words"

    word = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    correctAnswers = models.PositiveIntegerField(default=0)
    clues = models.ForeignKey(OneshotClues, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.word

class OneshotWordEasy(models.Model):
    class Meta: 
        verbose_name = "Oneshot Easy Daily Word"
        verbose_name_plural = "Oneshot Easy Daily Words"

    word = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    correctAnswers = models.PositiveIntegerField(default=0)
    clues = models.ForeignKey(OneshotClues, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.word
    

class Word(models.Model):
    class Meta: 
        verbose_name = "Word"
        verbose_name_plural = "Words"

    word = models.CharField(max_length=5)
    frequency = models.PositiveBigIntegerField(default=0)
    lastOccurance = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.word

class WordsHard(models.Model):
    class Meta: 
        verbose_name = "Hard Word"
        verbose_name_plural = "Hard Words"

    word = models.CharField(max_length=6)
    frequency = models.PositiveBigIntegerField(default=0)
    lastOccurance = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.word

class Guessle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Word Attempt"
        verbose_name_plural = "Word Attempts"
    word = models.ForeignKey(OneshotWord, on_delete=models.CASCADE)
    guess = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.word

class EasyGuessle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Easy Word Attempt"
        verbose_name_plural = "Easy Words Attempts"
    word = models.ForeignKey(OneshotWord, on_delete=models.CASCADE)
    guess = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)

class HardGuessle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Hard Word Attempt"
        verbose_name_plural = "Hard Words Attempts"
    word = models.ForeignKey(OneshotWord, on_delete=models.CASCADE)
    guess = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)

class Daily_Stars(models.Model):
    class Meta:
        verbose_name = "Daily Star Count"
        verbose_name_plural = "Daily Stars"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)
    stars = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.user.username