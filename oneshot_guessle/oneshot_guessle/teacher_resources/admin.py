from django.contrib import admin

from .models import Resource, Purchase

# Register your models here.
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'keystage', 'exam_board', 'price'] 
    search_fields = ['name', 'description', 'keystage', 'exam_board'] 
    list_filter = ['keystage', 'exam_board']  # Filter by these fields 

admin.site.register(Resource, ResourceAdmin)

class PurchaseAdmin(admin.ModelAdmin):
    def get_resource_name(self, obj):
        return obj.resource.name

    list_display = ['get_resource_name','user', 'purchase_date']  # Display these fields
    search_fields = ['user__username']  # Allow searching by username
    list_filter = ['user']  # Filter by user


admin.site.register(Purchase, PurchaseAdmin)