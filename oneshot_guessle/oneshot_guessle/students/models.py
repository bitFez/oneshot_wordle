from django.db import models
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class SheetsTab(models.Model):
    year = models.IntegerField() # eg 2527
    json_workbook = models.URLField(default=dict, blank=True)
    ks = models.CharField(max_length=3) # eg ks4
    week_tests_analysis = models.CharField(max_length=50)
    weekly_tests = models.CharField(max_length=50)
    mocks_analysis = models.CharField(max_length=50)
    mocks = models.CharField(max_length=50) 

    def __str__(self) -> str:
        return f"{self.year}-{self.ks}"