from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import re

User = get_user_model()


def default_answer_flags():
    return ["trim", "lowercase"]

class Puzzle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # e.g., "1447-1a hijri year-day and puzzle a or b"
    release_at = models.DateTimeField(db_index=True)
    description = models.TextField(blank=True)
    success_message = models.TextField(blank=True)
    accepted_answers = models.JSONField(default=list)  # canonical answers
    answer_flags = models.JSONField(
        default=default_answer_flags,
        blank=True,
        help_text=(
            "Answer normalization flags. Available: trim, lowercase, collapse_spaces, strip_all_spaces. "
            "Example: [\"trim\", \"lowercase\"]"
        ),
    )
    prerequisites = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="unlocks"
    )
    sequence = models.PositiveSmallIntegerField(default=0)  # optional: ordering within a day/group
    def __str__(self):
        return f"{self.slug}-{self.sequence}-{self.title}"
    
    def is_released(self):
        return timezone.now() >= self.release_at

    def check_answer(self, raw_answer: str) -> bool:
        # Answer flags control normalization. For example:
        # - trim: removes only leading/trailing whitespace
        # - collapse_spaces: reduces internal whitespace runs to a single space
        # - strip_all_spaces: removes all whitespace everywhere
        flags = set(self.answer_flags or [])

        def normalize(text: str) -> str:
            base = str(text or "")
            if "trim" in flags:
                base = base.strip()
            if "lowercase" in flags:
                base = base.lower()
            if "collapse_spaces" in flags:
                base = re.sub(r"\s+", " ", base)
            if "strip_all_spaces" in flags:
                base = re.sub(r"\s+", "", base)
            return base

        norm = normalize(raw_answer)
        return any(norm == normalize(a) for a in self.accepted_answers)

    def is_available_for(self, user):
        from django.utils import timezone
        if not self.is_released():
            return False
        if not user or not user.is_authenticated:
            return False
        for pre in self.prerequisites.all():
            if not Submission.objects.filter(puzzle=pre, user=user, is_correct=True).exists():
                return False
        return True
    

class Submission(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["puzzle", "user"], name="one_submission_per_user_per_puzzle")
        ]
    
    def __str__(self):
        return f"{self.puzzle.slug}-{self.user.username}-{'correct' if self.is_correct else 'incorrect'}"