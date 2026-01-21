from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponse
from django.conf import settings

from .models import Puzzle, Submission


def c_index(request):
    puzzles = Puzzle.objects.order_by('release_at')[:50]
    return render(request, 'pages/c_cipher/index.html', {'puzzles': puzzles})


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

    if request.method == 'POST':
        if not user:
            return HttpResponse('Login required to submit', status=403)
        answer = request.POST.get('answer', '')
        is_correct = puzzle.check_answer(answer)
        try:
            sub = Submission.objects.create(puzzle=puzzle, user=user, answer=answer, is_correct=is_correct)
        except IntegrityError:
            # user already submitted
            message = 'You have already submitted for this puzzle.'
        else:
            message = 'Correct!' if is_correct else 'Incorrect.'

    existing = None
    if user:
        existing = Submission.objects.filter(puzzle=puzzle, user=user).first()

    return render(request, 'c_cipher/puzzle_detail.html', {
        'puzzle': puzzle,
        'existing': existing,
        'message': message,
    })