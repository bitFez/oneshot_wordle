from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
User = get_user_model()

from .models import Puzzle, Submission

def c_about(request):
    return render(request, 'pages/c_cipher/about.html')

def c_index(request, hijri_year=None):
        
    # use hijri_year arg or get the latest hijri_year from released puzzles
    latest_hijri_year = None
    if hijri_year:
        puzzles = Puzzle.objects.filter(
            hijri_year=hijri_year,
            release_at__lte=timezone.now(),
            sequence=0
        ).order_by('release_at')[:50]
        latest_hijri_year = hijri_year
    else:
        latest_released_puzzle = Puzzle.objects.filter(
            release_at__lte=timezone.now()
        ).order_by('-release_at').values_list('hijri_year', flat=True).first()
        if latest_released_puzzle:
            puzzles = Puzzle.objects.filter(hijri_year=latest_released_puzzle, release_at__lte=timezone.now(), sequence=0).order_by('release_at')[:50]
            latest_hijri_year = latest_released_puzzle
        else:
            puzzles = Puzzle.objects.none()

    # Get solved puzzle IDs for the current user
    solved_puzzle_ids = set()
    attempted_puzzle_ids = set()
    if request.user.is_authenticated:
        solved_puzzle_ids = set(
            Submission.objects.filter(
                user=request.user,
                is_correct=True,
                puzzle__in=puzzles
            ).values_list('puzzle_id', flat=True)
        )
        attempted_puzzle_ids = set(
            Submission.objects.filter(
                user=request.user,
                is_correct=False,
                puzzle__in=puzzles
            ).values_list('puzzle_id', flat=True)
        )
    
    context = {
        'puzzles': puzzles,
        'latest_hijri_year': latest_hijri_year,
        'solved_puzzle_ids': solved_puzzle_ids,
        'attempted_puzzle_ids': attempted_puzzle_ids,
    }

    # Score for specific hijri year
    if request.user.is_authenticated:
        year_score = Submission.objects.filter(
            user=request.user, 
            is_correct=True, 
            puzzle__hijri_year=hijri_year if hijri_year else latest_hijri_year
        ).count()


        # Total score across all years
        total_score = Submission.objects.filter(
            user=request.user, 
            is_correct=True
        ).count()

        context['year_score'] = year_score
        context['total_score'] = total_score

    return render(request, 'pages/c_cipher/index.html', context)


@staff_member_required
def c_preview_hijri_year(request, hijri_year):
    """Preview template for a specific hijri_year (admin only)."""
    puzzles = Puzzle.objects.filter(hijri_year=hijri_year, sequence=0).order_by('release_at')[:50]
    
    # Get solved puzzle IDs for the current user
    solved_puzzle_ids = set(
        Submission.objects.filter(
            user=request.user,
            is_correct=True,
            puzzle__in=puzzles
        ).values_list('puzzle_id', flat=True)
    )
    
    # Get attempted (but not solved) puzzle IDs
    attempted_puzzle_ids = set(
        Submission.objects.filter(
            user=request.user,
            is_correct=False,
            puzzle__in=puzzles
        ).values_list('puzzle_id', flat=True)
    )
    
    return render(request, 'pages/c_cipher/index.html', {
        'preview_hijri_year': hijri_year,
        'puzzles': puzzles,
        'solved_puzzle_ids': solved_puzzle_ids,
        'attempted_puzzle_ids': attempted_puzzle_ids,
    })


def c_puzzle_view(request, slug):
    """View a puzzle by slug and allow submission."""
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
    if existing and existing.is_correct and user:
        next_puzzles = [p for p in puzzle.unlocks.order_by('release_at', 'sequence') if p.is_available_for(user)]

    return render(request, 'c_cipher/puzzle_detail.html', {
        'puzzle': puzzle,
        'existing': existing,
        'message': message,
        'next_puzzles': next_puzzles,
    })


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