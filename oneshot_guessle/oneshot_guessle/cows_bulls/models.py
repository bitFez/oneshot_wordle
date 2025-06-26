from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class DailyOCB(models.Model):
    """
    Model to store the daily One-Shot Cows and Bulls game.
    """
    date = models.DateField(unique=True)
    number = models.CharField(max_length=5, unique=True)
    clue1 = models.CharField(max_length=5, blank=True, null=True) # nothing is correct
    clue2 = models.CharField(max_length=5, blank=True, null=True) # one digit is correct but in the wrong place
    clue3 = models.CharField(max_length=5, blank=True, null=True) # one digit is correct and in the right place
    clue4 = models.CharField(max_length=5, blank=True, null=True) # two digits are correct but in the wrong place

    def __str__(self):
        return f"#{self.id} - {self.date}"
    
    class Meta:
        verbose_name = "Daily One-Shot Cows and Bulls"
        verbose_name_plural = "Daily One-Shot Cows and Bulls"

class DailyOCBAttempt(models.Model):
    """
    Model to store attempts for the daily One-Shot Cows and Bulls game.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ocb = models.ForeignKey(DailyOCB, on_delete=models.CASCADE)
    guess = models.CharField(max_length=5)
    cows = models.IntegerField(default=0)
    bulls = models.IntegerField(default=0)
    points_awarded = models.IntegerField(default=0) 
    
    attempt_number = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True) # Good to have for ordering attempts

    def __str__(self):
        return f"{self.user.username} - {self.ocb.date} - Guess: {self.guess} - Score: {self.points_awarded}"
    
    class Meta:
        verbose_name = "Daily Cows and Bulls Attempt"
        verbose_name_plural = "Daily Cows and Bulls Attempts"
        #unique_together = ('user', 'ocb')  # Ensure one attempt per user per day
        ordering = ['timestamp'] # ordering to easily retrieve attempts in order