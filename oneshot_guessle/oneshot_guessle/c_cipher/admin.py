from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.
from .models import Puzzle, Submission

class PuzzleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'release_at', 'sequence', 'view_puzzle_link')
    search_fields = ('title', 'slug')

    def view_puzzle_link(self, obj):
        if obj.slug:
            url = reverse('c_cipher:puzzle_preview', kwargs={'slug': obj.slug})
            return format_html('<a href="{}" target="_blank">View Puzzle ↗</a>', url)
        return "—"
    view_puzzle_link.short_description = 'Link'
    view_puzzle_link.allow_tags = True
	
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Submission)