from django.contrib import admin
from .models import DailyTangle, TangleAttempt
# Register your models here.

class DailyTangleAdmin(admin.ModelAdmin):
    model = DailyTangle
    search_fields = ('id',)
    list_filter =('date',)
    list_display = ('id','date',  )

class TangleAttemptAdmin(admin.ModelAdmin):
    model = TangleAttempt
    search_fields = ('user', 'tangle__id', 'words')
    list_filter = ('created_at',)
    list_display = ('user', 'tangle', 'words', 'created_at')

admin.site.register(DailyTangle, DailyTangleAdmin)
admin.site.register(TangleAttempt, TangleAttemptAdmin)