from django.contrib import admin

from .models import Word, OneshotWord, OneshotClues, Wordle_Attempt
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

class OneshotCluesAdmin(admin.ModelAdmin):
    model = OneshotClues
    search_fields = ('id', 'date',)
    list_filter =('date',)
    list_display = ('id','clue1','clue2','clue3','clue4','clue5','date', )

class Wordle_AttemptAdmin(admin.ModelAdmin):
    model = Wordle_Attempt
    search_fields = ('user', 'date','word',)
    list_filter =('date','user', 'word',)
    list_display = ('date','user', 'word', 'guess')

admin.site.register(Word, WordAdmin)
admin.site.register(OneshotWord, OneshotWordAdmin)
admin.site.register(OneshotClues, OneshotCluesAdmin)
admin.site.register(Wordle_Attempt, Wordle_AttemptAdmin)