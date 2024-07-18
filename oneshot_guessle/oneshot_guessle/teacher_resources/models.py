from django.db import models
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
KS_CHOICES = (
  ('ks3', 'KS5'),
  ('ks4', 'KS4'),
  ('ks5', 'KS5'),
)

CATEGORY_CHOICES = (
  ('ks3', 'KS5'),
  ('ks4', 'KS4'),
  ('ks5', 'KS5'),
)

EXAM_B_CHOICES = (
  ('ocr', 'OCR'),
  ('aqa', 'AQA'),
)

class Resource(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    keystage = models.CharField(max_length=20, choices=KS_CHOICES)
    exam_board = models.CharField(max_length=20, choices=EXAM_B_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resource_id = models.ForeignKey(Resource, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id
    
