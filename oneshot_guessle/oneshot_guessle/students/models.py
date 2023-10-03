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