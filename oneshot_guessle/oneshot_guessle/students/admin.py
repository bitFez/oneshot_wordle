from django.contrib import admin
from .models import Student

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
  list_display = ['user', 'examNo', 'exam_yr']
  list_filter = ['user', 'examNo','exam_yr']  # Filter by exam year

admin.site.register(Student, StudentAdmin)