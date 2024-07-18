from django.contrib import admin

from .models import Resource, Purchase

# Register your models here.
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'keystage', 'exam_board', 'category', 'price']
    search_fields = ['name', 'description', 'keystage', 'exam_board', 'category']
    list_filter = ['keystage', 'exam_board', 'category']  # Filter by these fields

admin.site.register(Resource, ResourceAdmin)

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'purchase_date']  # Display these fields
    search_fields = ['user__username']  # Allow searching by username
    list_filter = ['user']  # Filter by user

admin.site.register(Purchase, PurchaseAdmin)