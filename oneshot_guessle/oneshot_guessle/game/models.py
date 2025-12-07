from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class OneshotClues(models.Model):
    class Meta: 
        verbose_name = "Oneshot Regular Clue"
        verbose_name_plural = "Oneshot Regular Clues"
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
        verbose_name = "Oneshot Easy Clue"
        verbose_name_plural = "OneshotEasy Clues"
    clue1 = models.CharField(max_length=5)
    clue2 = models.CharField(max_length=5)
    clue3 = models.CharField(max_length=5)
    clue4 = models.CharField(max_length=5)
    clue5 = models.CharField(max_length=5)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date)

class OneshotCluesHard(models.Model):
    class Meta: 
        verbose_name = "Oneshot Hard Clue"
        verbose_name_plural = "Oneshot Hard Clues"
    clue1 = models.CharField(max_length=6)
    clue2 = models.CharField(max_length=6)
    clue3 = models.CharField(max_length=6)
    clue4 = models.CharField(max_length=6)
    clue5 = models.CharField(max_length=6)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date)

class OneshotWord(models.Model):
    class Meta: 
        verbose_name = "Oneshot Regular Daily Word"
        verbose_name_plural = "Oneshot Regular Daily Words"

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
    clues = models.ForeignKey(OneshotCluesEasy, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.word

class OneshotWordHard(models.Model):
    class Meta: 
        verbose_name = "Oneshot Hard Daily Word"
        verbose_name_plural = "Oneshot Hard Daily Words"

    word = models.CharField(max_length=6)
    date = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    correctAnswers = models.PositiveIntegerField(default=0)
    clues = models.ForeignKey(OneshotCluesHard, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.word
    

class Word(models.Model):
    """ 5 letter words """
    class Meta: 
        verbose_name = "5 Letter Word"
        verbose_name_plural = "5 Letter Words"

    word = models.CharField(max_length=5)
    frequency = models.PositiveBigIntegerField(default=0)
    lastOccurance = models.DateTimeField(auto_now=True, null=True)
    proper_noun = models.BooleanField(default=True)

    def __str__(self):
        return self.word

class WordsHard(models.Model):
    """ 6 letter words """
    class Meta: 
        verbose_name = "6 letter Word (Hard)"
        verbose_name_plural = "6 letter Words (Hard)"

    word = models.CharField(max_length=6)
    frequency = models.PositiveBigIntegerField(default=0)
    lastOccurance = models.DateTimeField(auto_now=True, null=True)
    proper_noun = models.BooleanField(default=True)

    def __str__(self):
        return self.word

class Guessle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Regular Guessle Word Attempt"
        verbose_name_plural = "Regular Guessle Word Attempts"
    word = models.ForeignKey(OneshotWord, on_delete=models.CASCADE)
    guess = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)

    # def __str__(self):
    #     return self.word

class EasyGuessle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Easy Guessle Word Attempt"
        verbose_name_plural = "Easy Guessle Words Attempts"
    word = models.ForeignKey(OneshotWordEasy, on_delete=models.CASCADE)
    guess = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)

class HardGuessle_Attempt(models.Model):
    class Meta: 
        verbose_name = "Hard Guessle Word Attempt"
        verbose_name_plural = "Hard Guessle Words Attempts"
    word = models.ForeignKey(OneshotWordHard, on_delete=models.CASCADE)
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