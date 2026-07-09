from django.db import models
from django.contrib.auth import get_user_model
import json
User = get_user_model()

# Create your models here.
class DailyOCB(models.Model):
    """
    Model to store the daily One-Shot Cows and Bulls game.
    """
    date = models.DateField(unique=True)
    challenge_number = models.IntegerField(unique=True, null=True, blank=True)  # Sequential challenge number
    number = models.CharField(max_length=5, unique=True)
    clue1 = models.CharField(max_length=5, blank=True, null=True) # nothing is correct
    clue2 = models.CharField(max_length=5, blank=True, null=True) # one digit is correct but in the wrong place
    clue3 = models.CharField(max_length=5, blank=True, null=True) # one digit is correct and in the right place
    clue4 = models.CharField(max_length=5, blank=True, null=True) # two digits are correct but in the wrong place

    def __str__(self):
        return f"#Challenge {self.challenge_number or self.id} - {self.date}"
    
    class Meta:
        verbose_name = "Daily One-Shot Cows and Bulls"
        verbose_name_plural = "Daily One-Shot Cows and Bulls"
        ordering = ['-challenge_number']

class DailyOCBAttempt(models.Model):
    """
    Model to store attempts for the daily One-Shot Cows and Bulls game.
    Stores all attempts as a JSON array in a single record per user per puzzle.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ocb = models.ForeignKey(DailyOCB, on_delete=models.CASCADE)
    attempts = models.JSONField(default=list, help_text="Array of {guess, cows, bulls, attempt_number}")
    is_solved = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    solved_on_attempt = models.IntegerField(default=None, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.ocb.date} - Attempts: {len(self.attempts)}"
    
    class Meta:
        verbose_name = "Daily Cows and Bulls Attempt"
        verbose_name_plural = "Daily Cows and Bulls Attempts"
        unique_together = ('user', 'ocb')  # One record per user per puzzle
        ordering = ['-timestamp']