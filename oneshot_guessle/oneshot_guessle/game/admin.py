from django.contrib import admin

from .models import Word, OneshotWord, OneshotWordEasy, OneshotClues, Guessle_Attempt, Daily_Stars, EasyGuessle_Attempt
# Register your models here.

class WordAdmin(admin.ModelAdmin):
    model = OneshotWord
    search_fields = ('id', 'word','lastOccurance',)
    list_filter =('frequency','lastOccurance',)
    list_display = ('id','word','frequency','lastOccurance', )

class OneshotWordAdmin(admin.ModelAdmin):
    model = Word
    search_fields = ('id', 'word','date','attempts','correctAnswers',)
    list_filter =('word','date','attempts','correctAnswers',)
    list_display = ('id','word','date','attempts','correctAnswers', )

class OneshotWordEasyAdmin(admin.ModelAdmin):
    model = OneshotWordEasy
    search_fields = ('id', 'word','date','attempts','correctAnswers',)
    list_filter =('word','date','attempts','correctAnswers',)
    list_display = ('id','word','date','attempts','correctAnswers', )

class OneshotCluesAdmin(admin.ModelAdmin):
    model = OneshotClues
    search_fields = ('id', 'date',)
    list_filter =('date',)
    list_display = ('id','clue1','clue2','clue3','clue4','clue5','date', )

class EasyGuessle_AttemptAdmin(admin.ModelAdmin):
    model = EasyGuessle_Attempt
    search_fields = ('user', 'date','word',)
    list_filter =('date','user', 'word',)
    list_display = ('date','user', 'word', 'guess')

class Daily_StarsAdmin(admin.ModelAdmin):
    model = Daily_Stars
    search_fields = ('user', 'date','stars',)
    list_filter = ('user', 'date','stars',)
    list_display = ('user', 'date','stars',)


admin.site.register(Word, WordAdmin)
admin.site.register(OneshotWord, OneshotWordAdmin)
admin.site.register(OneshotWordEasy, OneshotWordEasyAdmin)
admin.site.register(OneshotClues, OneshotCluesAdmin)
admin.site.register(Guessle_Attempt, Guessle_AttemptAdmin)
admin.site.register(Daily_Stars, Daily_StarsAdmin)