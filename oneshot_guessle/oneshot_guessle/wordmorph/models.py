from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class WordMorph(models.Model):

    class Meta: 
        verbose_name = "Word Morph Daily Word"
        verbose_name_plural = "Word Morph Daily Words"
    morph_number = models.PositiveIntegerField(null=True, blank=True, unique=True, help_text="Override the displayed puzzle number. Leave blank to use the database ID.")
    start_word = models.CharField(max_length=5)
    end_word = models.CharField(max_length=5)
    total_attempts = models.PositiveIntegerField(default=0)
    least_morphs = models.PositiveIntegerField(default=0)
    most_morphs = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return str(self.morph_number) if self.morph_number else str(self.pk)
    

class Morph_Attempt(models.Model):
    class Meta: 
        verbose_name = "Word Morph Attempt"
        verbose_name_plural = "Word Morph Attempts"
    word = models.ForeignKey(WordMorph, on_delete=models.CASCADE)
    guess = models.JSONField(default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, null=True)
    morph_count = models.PositiveIntegerField(default=0)
