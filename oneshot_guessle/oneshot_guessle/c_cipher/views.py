from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from .models import Puzzle, Submission

def c_about(request):
    return render(request, 'pages/c_cipher/about.html')

def c_index(request):
    puzzles = Puzzle.objects.order_by('release_at')[:50]
    
    # Get the latest hijri_year from released puzzles
    latest_hijri_year = None
    latest_released_puzzle = Puzzle.objects.filter(
        release_at__lte=timezone.now()
    ).order_by('-release_at').values_list('hijri_year', flat=True).first()
    
    if latest_released_puzzle:
        latest_hijri_year = latest_released_puzzle
    
    return render(request, 'pages/c_cipher/index.html', {
        'puzzles': puzzles,
        'latest_hijri_year': latest_hijri_year,
    })


@staff_member_required
def c_preview_hijri_year(request, hijri_year):
    """Preview template for a specific hijri_year (admin only)."""
    return render(request, 'pages/c_cipher/index.html', {
        'preview_hijri_year': hijri_year,
    })


def c_puzzle_view(request, year, day):
    # Placeholder: production view should locate puzzle by date/sequence.
    return HttpResponse(status=204)


def c_puzzle_preview(request, slug):
    """Developer preview: load a puzzle by slug and allow submission regardless of release/prereqs."""
    # Restrict preview: allow only in DEBUG or to staff users
    if not settings.DEBUG and not (request.user.is_authenticated and request.user.is_staff):
        return HttpResponse('Preview not allowed', status=403)

    puzzle = get_object_or_404(Puzzle, slug=slug)

    user = request.user if request.user.is_authenticated else None

    message = None

    existing = None
    if user:
        existing = Submission.objects.filter(puzzle=puzzle, user=user).first()

    if request.method == 'POST':
        if not user:
            return HttpResponse('Login required to submit', status=403)
        answer = request.POST.get('answer', '')
        is_correct = puzzle.check_answer(answer)

        if existing and existing.is_correct:
            message = 'You have already solved this puzzle.'
        else:
            if existing:
                existing.answer = answer
                existing.is_correct = is_correct
                existing.save(update_fields=["answer", "is_correct"])
            else:
                existing = Submission.objects.create(
                    puzzle=puzzle,
                    user=user,
                    answer=answer,
                    is_correct=is_correct,
                )
            message = 'Correct!' if is_correct else 'Incorrect. Try again.'

    next_puzzles = []
    if settings.DEBUG or (user and user.is_staff):
        next_puzzles = list(puzzle.unlocks.order_by('release_at', 'sequence'))
    elif existing and existing.is_correct and user:
        next_puzzles = [p for p in puzzle.unlocks.order_by('release_at', 'sequence') if p.is_available_for(user)]

    return render(request, 'c_cipher/puzzle_detail.html', {
        'puzzle': puzzle,
        'existing': existing,
        'message': message,
        'next_puzzles': next_puzzles,
    })