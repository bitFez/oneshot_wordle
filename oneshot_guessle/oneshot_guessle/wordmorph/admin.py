from django.contrib import admin

from .models import Morph_Attempt, WordMorph


class MorphAttemptInline(admin.TabularInline):
	model = Morph_Attempt
	extra = 0
	fields = ("user", "morph_count", "date", "guess")
	readonly_fields = ("date",)
	autocomplete_fields = ("user",)


@admin.register(WordMorph)
class WordMorphAdmin(admin.ModelAdmin):
	model = WordMorph
	inlines = [MorphAttemptInline]
	search_fields = ("id", "morph_number", "start_word", "end_word", "date")
	list_filter = ("date", "total_attempts", "least_morphs", "most_morphs")
	list_display = ("id", "morph_number", "start_word", "end_word", "total_attempts", "least_morphs", "most_morphs", "date")
	list_editable = ("morph_number",)
	readonly_fields = ("date",)


@admin.register(Morph_Attempt)
class MorphAttemptAdmin(admin.ModelAdmin):
	model = Morph_Attempt
	search_fields = ("user__username", "word__start_word", "word__end_word", "date")
	list_filter = ("date", "user", "word", "morph_count")
	list_display = ("date", "user", "word", "morph_count")
	autocomplete_fields = ("user", "word")
