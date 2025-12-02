from django.db import models
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    examNo = models.IntegerField(null=True)
    exam_yr = models.IntegerField(null=True)

    def __str__(self):
        return self.user.username
    
    # def get_absolute_url(self):
    #     return reverse("students:profile_detail", kwargs={'id':self.id})

class SheetsTab(models.Model):
    year = models.IntegerField()
    ks = models.CharField(max_length=3)
    week_tests_analysis = models.CharField(max_length=50)
    weekly_tests = models.CharField(max_length=50)
    mocks_analysis = models.CharField(max_length=50)
    mocks = models.CharField(max_length=50) 

    def __str__(self) -> str:
        return f"{self.year}-{self.ks}"