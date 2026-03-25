from django.core.management.base import BaseCommand
from django.db.models import F
from oneshot_guessle.game.models import OneshotWord, OneshotWordEasy, OneshotWordHard


class Command(BaseCommand):
    help = 'Auto-number existing guessle puzzles in chronological order'

    def handle(self, *args, **options):
        models = [
            ('OneshotWord', OneshotWord),
            ('OneshotWordEasy', OneshotWordEasy),
            ('OneshotWordHard', OneshotWordHard),
        ]

        for model_name, model in models:
            # Get all records without a puzzle_number, ordered by date
            records = model.objects.filter(puzzle_number__isnull=True).order_by('date')
            
            if not records.exists():
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {model_name}: No records to autonumber')
                )
                continue
            
            # Assign puzzle numbers starting from 1
            for index, record in enumerate(records, start=1):
                record.puzzle_number = index
                record.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {model_name}: Auto-numbered {len(records)} puzzles (1-{len(records)})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n✅ All puzzles have been auto-numbered in chronological order!')
        )
