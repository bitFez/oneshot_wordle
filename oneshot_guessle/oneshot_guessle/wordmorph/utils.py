from django.core.management.base import CommandError
from django.db.models import Max

from oneshot_guessle.game.views import get_random_word
from oneshot_guessle.wordmorph.models import WordMorph


def next_morph_number():
    return (WordMorph.objects.aggregate(Max("morph_number"))["morph_number__max"] or 0) + 1


def word_distance(left_word, right_word):
    left = str(left_word or "").lower()
    right = str(right_word or "").lower()
    if len(left) != len(right):
        return None
    return sum(1 for left_letter, right_letter in zip(left, right) if left_letter != right_letter)


def pick_easier_end_word(start_word_obj, max_letter_changes=2, attempts=60):
    start_word = str(getattr(start_word_obj, "word", start_word_obj)).lower()

    fallback_candidate = None
    for _ in range(attempts):
        candidate = get_random_word()
        if not candidate:
            continue

        candidate_word = str(getattr(candidate, "word", candidate)).lower()
        if candidate_word == start_word:
            continue

        distance = word_distance(start_word, candidate_word)
        if distance is None:
            continue

        if distance <= max_letter_changes:
            return candidate

        if fallback_candidate is None:
            fallback_candidate = candidate

    if fallback_candidate is not None:
        return fallback_candidate

    return get_random_word()


def generate_daily_wordmorph(today_date, max_letter_changes=2):
    existing = WordMorph.objects.filter(date__date=today_date).first()
    if existing:
        return existing, False

    start_word_obj = get_random_word()
    if not start_word_obj:
        raise CommandError("Could not generate WordMorph puzzle: no eligible 5-letter start word found")

    end_word_obj = pick_easier_end_word(start_word_obj, max_letter_changes=max_letter_changes)
    if not end_word_obj or start_word_obj.word == end_word_obj.word:
        raise CommandError("Could not generate WordMorph puzzle: no eligible 5-letter end word found")

    wordmorph = WordMorph.objects.create(
        start_word=start_word_obj.word,
        end_word=end_word_obj.word,
        morph_number=next_morph_number(),
    )
    return wordmorph, True