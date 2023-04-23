from django.contrib import admin

from .models import Word, OneshotWord
# Register your models here.

class WordAdmin(admin.ModelAdmin):
    model = Word
    search_fields = ('id', 'word','lastOccurance',)
    list_filter =('frequency','lastOccurance',)
    list_display = ('id','word','frequency','lastOccurance', )

class OneshotWordAdmin(admin.ModelAdmin):
    model = Word
    search_fields = ('id', 'word','date','attempts','correctAnswers',)
    list_filter =('word','date','attempts','correctAnswers',)
    list_display = ('id','word','date','attempts','correctAnswers', )

admin.site.register(Word, WordAdmin)
admin.site.register(OneshotWord, OneshotWordAdmin)