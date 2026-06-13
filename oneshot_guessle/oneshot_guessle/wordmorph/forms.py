import re

from django import forms
from django.core.exceptions import ValidationError

from oneshot_guessle.game.models import Word


def _one_letter_apart(left_word, right_word):
    if len(left_word) != len(right_word):
        return False
    differences = sum(
        1 for left_letter, right_letter in zip(left_word, right_word) if left_letter != right_letter
    )
    return differences == 1


class MorphSubmissionForm(forms.Form):
    morph_chain = forms.CharField(
        label="Morph chain",
        widget=forms.Textarea(
            attrs={
                "class": "form-control form-control-lg",
                "rows": 5,
                "placeholder": "Enter each word on a new line or separated by spaces",
            }
        ),
        help_text="Include the start word first and the end word last.",
    )

    def __init__(self, *args, puzzle=None, **kwargs):
        self.puzzle = puzzle
        super().__init__(*args, **kwargs)

    def clean_morph_chain(self):
        raw_value = self.cleaned_data["morph_chain"]
        words = [piece.strip().lower() for piece in re.split(r"[\s,]+", raw_value) if piece.strip()]

        if len(words) < 2:
            raise ValidationError("Enter at least the start word and the end word.")

        self.cleaned_data["parsed_chain"] = words
        return raw_value

    def clean(self):
        cleaned_data = super().clean()
        puzzle = self.puzzle
        words = cleaned_data.get("parsed_chain", [])

        if not puzzle:
            raise ValidationError("No active WordMorph puzzle is available.")

        if not words:
            return cleaned_data

        if words[0] != puzzle.start_word.lower():
            raise ValidationError(f"Your chain must start with {puzzle.start_word.upper()}.")

        if words[-1] != puzzle.end_word.lower():
            raise ValidationError(f"Your chain must end with {puzzle.end_word.upper()}.")

        if any(len(word) != 5 for word in words):
            raise ValidationError("Every word in the chain must be exactly 5 letters long.")

        valid_words = set(Word.objects.filter(word__in=words).values_list("word", flat=True))
        missing_words = [word for word in words if word not in valid_words]
        if missing_words:
            raise ValidationError(
                "Invalid word(s): " + ", ".join(word.upper() for word in missing_words)
            )

        for left_word, right_word in zip(words, words[1:]):
            if not _one_letter_apart(left_word, right_word):
                raise ValidationError(
                    f"{left_word.upper()} and {right_word.upper()} must differ by exactly one letter."
                )

        cleaned_data["morph_chain_words"] = words
        return cleaned_data