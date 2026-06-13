from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from oneshot_guessle.wordmorph.utils import generate_daily_wordmorph


class Command(BaseCommand):
    help = "Generate today's WordMorph daily puzzle if it does not already exist"

    easy_max_letter_changes = 2

    def handle(self, *args, **options):
        today_date = timezone.localdate()

        self.stdout.write(f"Generating daily WordMorph puzzle for {today_date}...")

        wordmorph_obj, created = generate_daily_wordmorph(today_date, max_letter_changes=self.easy_max_letter_changes)

        self.stdout.write(
            self.style.SUCCESS(
                "Done. " f"WordMorph={'created' if created else 'exists'}"
            )
        )
