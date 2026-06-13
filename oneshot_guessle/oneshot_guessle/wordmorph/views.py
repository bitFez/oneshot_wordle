from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render
from django.utils import timezone

from oneshot_guessle.wordmorph.forms import MorphSubmissionForm
from oneshot_guessle.wordmorph.models import Morph_Attempt, WordMorph
from oneshot_guessle.wordmorph.utils import generate_daily_wordmorph

# Create your views here.
@login_required
def morph_index(request):
    today = timezone.localdate()
    puzzle = WordMorph.objects.filter(date__date=today).first()

    if puzzle is None:
        try:
            puzzle, _created = generate_daily_wordmorph(today)
        except Exception:
            puzzle = WordMorph.objects.order_by("-date").first()

    if request.method == "POST":
        form = MorphSubmissionForm(request.POST, puzzle=puzzle)

        if puzzle is not None:
            WordMorph.objects.filter(pk=puzzle.pk).update(total_attempts=F("total_attempts") + 1)
            puzzle.refresh_from_db(fields=["total_attempts", "least_morphs", "most_morphs"])

        if form.is_valid() and puzzle is not None:
            chain = form.cleaned_data["morph_chain_words"]
            morph_count = max(0, len(chain) - 1)

            with transaction.atomic():
                if puzzle.least_morphs == 0 or morph_count < puzzle.least_morphs:
                    puzzle.least_morphs = morph_count

                if morph_count > puzzle.most_morphs:
                    puzzle.most_morphs = morph_count

                puzzle.save(update_fields=["least_morphs", "most_morphs"])

                Morph_Attempt.objects.create(
                    word=puzzle,
                    guess=chain,
                    user=request.user,
                    morph_count=morph_count,
                )

            messages.success(
                request,
                f"Chain saved. You used {morph_count} morphs across {len(chain)} words.",
            )
            return redirect("wordmorph:morph_index")

        if form.errors:
            messages.error(request, "Please fix the chain below and try again.")
    else:
        form = MorphSubmissionForm(puzzle=puzzle)

    context = {
        "puzzle": puzzle,
        "is_today": bool(puzzle and puzzle.date and puzzle.date.date() == today),
        "today": today,
        "form": form,
    }
    return render(request, "pages/wordmorph/wordmorph_index.html", context)