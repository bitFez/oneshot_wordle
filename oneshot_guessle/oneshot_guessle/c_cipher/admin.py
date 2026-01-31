from django.contrib import admin

# Register your models here.
from .models import Puzzle, Submission

admin.site.register(Puzzle)
admin.site.register(Submission)