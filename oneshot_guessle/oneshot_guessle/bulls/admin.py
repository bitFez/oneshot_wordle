from django.contrib import admin

from .models import DailyOCB, DailyOCBAttempt
# Register your models here.

@admin.register(DailyOCB)
class DailyOCBAdmin(admin.ModelAdmin):
    """
    Admin interface for the Daily Cows and Bulls game.
    """
    list_display = ('challenge_number', 'date', 'number', 'clue1', 'clue2', 'clue3', 'clue4')
    search_fields = ('date', 'number', 'challenge_number')
    ordering = ('-challenge_number',)
    list_filter = ('date',) 

@admin.register(DailyOCBAttempt)
class DailyOCBAttemptAdmin(admin.ModelAdmin):
    """
    Admin interface for the Daily Cows and Bulls attempts.
    """
    list_display = ('user', 'ocb', 'attempt_count', 'is_solved', 'solved_on_attempt', 'points_awarded')
    search_fields = ('user__username', 'ocb__date')
    ordering = ('-ocb__date', '-is_solved', '-points_awarded')
    list_filter = ('ocb__date', 'user', 'is_solved')
    raw_id_fields = ('user', 'ocb')
    readonly_fields = ('timestamp', 'updated_at', 'attempts')

    def attempt_count(self, obj):
        return len(obj.attempts)
    attempt_count.short_description = 'Total Attempts'

    

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