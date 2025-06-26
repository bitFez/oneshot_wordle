from django.contrib import admin

from .models import DailyOCB, DailyOCBAttempt
# Register your models here.

@admin.register(DailyOCB)
class DailyOCBAdmin(admin.ModelAdmin):
    """
    Admin interface for the Daily Cows and Bulls game.
    """
    list_display = ('date', 'number', 'clue1', 'clue2', 'clue3', 'clue4')
    search_fields = ('date', 'number')
    ordering = ('-date',)
    list_filter = ('date',) 

@admin.register(DailyOCBAttempt)
class DailyOCBAttemptAdmin(admin.ModelAdmin):
    """
    Admin interface for the Daily Cows and Bulls attempts.
    """
    list_display = ('user', 'ocb', 'guess', 'points_awarded', 'cows', 'bulls')
    search_fields = ('user__username', 'ocb__date', 'guess')
    ordering = ('-ocb__date', '-points_awarded')
    list_filter = ('ocb__date', 'user')
    raw_id_fields = ('user', 'ocb')

    

# Register the models with the admin site
# admin.site.register(DailyOCB, DailyOCBAdmin)
# admin.site.register(DailyOCBAttempt, DailyOCBAttemptAdmin)
try:
    admin.site.register(DailyOCB, DailyOCBAdmin)
except admin.sites.AlreadyRegistered:
    pass
try:
    admin.site.register(DailyOCBAttempt, DailyOCBAttemptAdmin)
except admin.sites.AlreadyRegistered:
    pass