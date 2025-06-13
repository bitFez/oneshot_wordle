from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


from .utils import SCRABBLE_LETTER_VALUES

class DailyTangle(models.Model):
    """
    Model to store the daily tangle words.
    """
    SCRABBLE_LETTER_VALUES = SCRABBLE_LETTER_VALUES  # Importing Scrabble letter values from constants

    word1 = models.CharField(max_length=12)  # Column 1
    word2 = models.CharField(max_length=12)  # Column 2
    word3 = models.CharField(max_length=12)  # Column 3
    word4 = models.CharField(max_length=12)  # Column 4
    word5 = models.CharField(max_length=12)  # Column 5
    word6 = models.CharField(max_length=12)  # Row 1
    word7 = models.CharField(max_length=12)  # Row 2
    word8 = models.CharField(max_length=12)  # Row 3
    word9 = models.CharField(max_length=12)  # Row 4
    date = models.DateField(auto_now_add=True, unique=True)

    def __str__(self):
        if self.date:  # Check if date exists
            return f"Tangle for {self.date.strftime('%Y-%m-%d')}"
        return f"Tangle (ID: {self.id})"
    
    class Meta:
        verbose_name = "Daily Tangle"
        verbose_name_plural = "Daily Tangles"
        ordering = ['-date']

    @classmethod
    def get_scrabble_value(cls, letter):
        """Returns the Scrabble point value for a single letter"""
        return cls.SCRABBLE_LETTER_VALUES.get(letter.upper(), 0)
    
    def get_column_words(self):
        return [self.word1, self.word2, self.word3, self.word4, self.word5]
    
    def get_row_words(self):
        return [self.word6, self.word7, self.word8, self.word9]
    
class TangleAttempt(models.Model):
    """
    Model to store the user's attempts for the daily tangle.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tangle = models.ForeignKey(DailyTangle, on_delete=models.CASCADE)
    words = models.JSONField() # store user attempts as a list of words
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)  # Points scored by the user

    def __str__(self):
        return f"{self.user} - {self.tangle} - {self.created_at}"
    
    class Meta:
        verbose_name = "Tangle Attempt"
        verbose_name_plural = "Tangle Attempts"
        ordering = ['-created_at'] 