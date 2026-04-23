from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.utils import timezone

from oneshot_guessle.game.bluesky import post_daily_main_puzzle_to_bluesky
from oneshot_guessle.game.functions import get_random_clues
from oneshot_guessle.game.models import (
    OneshotClues,
    OneshotCluesEasy,
    OneshotCluesHard,
    OneshotWord,
    OneshotWordEasy,
    OneshotWordHard,
    Word,
    WordsHard,
)
from oneshot_guessle.game.views import get_random_word


class Command(BaseCommand):
    help = "Generate today's main/easy/hard daily puzzles if they do not already exist"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-bluesky",
            action="store_true",
            help="Do not post the main daily puzzle to Bluesky even if enabled.",
        )

    def handle(self, *args, **options):
        skip_bluesky = options["skip_bluesky"]
        today_date = timezone.localdate()

        self.stdout.write(f"Generating daily puzzles for {today_date}...")

        main_obj, main_created, main_clues = self._ensure_main(today_date)
        easy_obj, easy_created = self._ensure_easy(today_date)
        hard_obj, hard_created = self._ensure_hard(today_date)

        if main_created and not skip_bluesky:
            previous_main = OneshotWord.objects.filter(date__date__lt=today_date).order_by("-date").first()
            previous_attempts = int(getattr(previous_main, "attempts", 0) or 0) if previous_main else 0
            previous_correct = int(getattr(previous_main, "correctAnswers", 0) or 0) if previous_main else 0

            posted = post_daily_main_puzzle_to_bluesky(
                puzzle_number=main_obj.puzzle_number or 0,
                target_word=str(main_obj.word or ""),
                clues=main_clues,
                attempts=previous_attempts,
                correct_answers=previous_correct,
            )
            msg = "posted" if posted else "skipped/failed"
            self.stdout.write(self.style.WARNING(f"Main Bluesky post: {msg}"))

        self.stdout.write(
            self.style.SUCCESS(
                "Done. "
                f"main={'created' if main_created else 'exists'}, "
                f"easy={'created' if easy_created else 'exists'}, "
                f"hard={'created' if hard_created else 'exists'}"
            )
        )

    def _normalize_clues(self, clue_texts, target_word, candidate_model):
        if isinstance(clue_texts, str):
            if " " in clue_texts:
                clue_texts = clue_texts.split()
            else:
                clue_texts = [clue_texts]

        if not isinstance(clue_texts, (list, tuple)):
            clue_texts = []

        clue_texts = [str(c or "").lower() for c in clue_texts]

        if len(clue_texts) < 5:
            fallback = []
            target_word = str(target_word or "").lower()
            for cand in candidate_model.objects.all():
                w = str(getattr(cand, "word", cand)).lower()
                if w != target_word and len(w) == len(target_word):
                    fallback.append(w)
                    if len(fallback) == 5:
                        break
            clue_texts = clue_texts + [c for c in fallback if c not in clue_texts]

        clue_texts = (clue_texts + [""] * 5)[:5]
        return clue_texts

    def _next_puzzle_number(self, model):
        return (model.objects.aggregate(Max("puzzle_number"))["puzzle_number__max"] or 0) + 1

    def _increment_frequency(self, word_obj):
        try:
            word_obj.frequency = (word_obj.frequency or 0) + 1
            word_obj.save()
        except Exception:
            pass

    def _ensure_main(self, today_date):
        existing = OneshotWord.objects.filter(date__date=today_date).first()
        if existing:
            clues = [
                str(getattr(existing.clues, "clue1", "") or ""),
                str(getattr(existing.clues, "clue2", "") or ""),
                str(getattr(existing.clues, "clue3", "") or ""),
                str(getattr(existing.clues, "clue4", "") or ""),
                str(getattr(existing.clues, "clue5", "") or ""),
            ]
            return existing, False, clues

        word_obj = get_random_word()
        if not word_obj:
            raise CommandError("Could not generate main puzzle: no eligible 5-letter word found")

        target_word = str(getattr(word_obj, "word", word_obj)).lower()
        clue_texts = get_random_clues(target_word, difficulty="regular")
        clue_texts = self._normalize_clues(clue_texts, target_word, Word)

        clues_obj = OneshotClues.objects.create(
            clue1=clue_texts[0],
            clue2=clue_texts[1],
            clue3=clue_texts[2],
            clue4=clue_texts[3],
            clue5=clue_texts[4],
        )

        oneshot = OneshotWord.objects.create(
            word=target_word,
            clues=clues_obj,
            puzzle_number=self._next_puzzle_number(OneshotWord),
        )
        self._increment_frequency(word_obj)
        return oneshot, True, clue_texts

    def _ensure_easy(self, today_date):
        existing = OneshotWordEasy.objects.filter(date__date=today_date).first()
        if existing:
            return existing, False

        word_obj = get_random_word()
        if not word_obj:
            raise CommandError("Could not generate easy puzzle: no eligible 5-letter word found")

        target_word = str(getattr(word_obj, "word", word_obj)).lower()
        clue_texts = get_random_clues(target_word, difficulty="easy")
        clue_texts = self._normalize_clues(clue_texts, target_word, Word)

        clues_obj = OneshotCluesEasy.objects.create(
            clue1=clue_texts[0],
            clue2=clue_texts[1],
            clue3=clue_texts[2],
            clue4=clue_texts[3],
            clue5=clue_texts[4],
        )

        oneshot = OneshotWordEasy.objects.create(
            word=target_word,
            clues=clues_obj,
            puzzle_number=self._next_puzzle_number(OneshotWordEasy),
        )
        self._increment_frequency(word_obj)
        return oneshot, True

    def _ensure_hard(self, today_date):
        existing = OneshotWordHard.objects.filter(date__date=today_date).first()
        if existing:
            return existing, False

        word_obj = get_random_word(difficulty="hard")
        if not word_obj:
            raise CommandError("Could not generate hard puzzle: no eligible 6-letter word found")

        target_word = str(getattr(word_obj, "word", word_obj)).lower()
        clue_texts = get_random_clues(target_word, difficulty="hard")
        clue_texts = self._normalize_clues(clue_texts, target_word, WordsHard)

        clues_obj = OneshotCluesHard.objects.create(
            clue1=clue_texts[0],
            clue2=clue_texts[1],
            clue3=clue_texts[2],
            clue4=clue_texts[3],
            clue5=clue_texts[4],
        )

        oneshot = OneshotWordHard.objects.create(
            word=target_word,
            clues=clues_obj,
            puzzle_number=self._next_puzzle_number(OneshotWordHard),
        )
        self._increment_frequency(word_obj)
        return oneshot, True
