from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
import os
import datetime
from django.conf import settings
from django.contrib.staticfiles.finders import find
from random import sample
from django.db.models import OuterRef, Subquery

# importing functions
from .functions.twl import check
from .models import DailyTangle, TangleAttempt

from .utils import process_valid_submissions
# Create your views here.

def tangle_index(request):
    today = datetime.date.today()
    tangle = DailyTangle.objects.filter(date=today).first()

    if not tangle:
        file_path = os.path.join(settings.BASE_DIR, 'oneshot_guessle', 'tangle', 'words', 'new_words.txt')
        try:
            with open(file_path, 'r') as f:
                word_list = [line.strip() for line in f if line.strip()]
            word_list = sample(word_list, 9)
            tangle = DailyTangle.objects.create(
                word1=word_list[0], word2=word_list[1], word3=word_list[2],
                word4=word_list[3], word5=word_list[4],
                word6=word_list[5], word7=word_list[6],
                word8=word_list[7], word9=word_list[8]
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find words file at: {file_path}")

    attempted = False
    previous_words_list = []
    modal_data = {}

    if request.user.is_authenticated:
        attempt = TangleAttempt.objects.filter(user=request.user, tangle=tangle).first()
        if attempt:
            attempted = True
            words = attempt.words
            score = attempt.points
            

            previous_words = {
                "word1": words.get("word1", "")[:5],
                "word2": words.get("word2", "")[:5],
                "word3": words.get("word3", "")[:5],
                "word4": words.get("word4", "")[:5],
            }
            previous_words_list = [list(word) for key, word in sorted(previous_words.items())]

            # Build modal data
            modal_data = {
                "score": score,
                "submitted_words": words,
            }

    context = {
        'tangle': tangle,
        'attempted': attempted,
        'previous_words': previous_words_list,
        'modal_data': modal_data,
    }
    return render(request, 'pages/tangle/tangle_index.html', context)


@require_POST
def submit_words(request):
    # 1️⃣ Fetch the tangle
    tangle_id = request.POST.get('tangle_id') or request.session.get('current_tangle_id')
    daily_tangle_instance = get_object_or_404(DailyTangle, id=tangle_id)

    # Check for existing attempt
    if request.user.is_authenticated:
        if TangleAttempt.objects.filter(user=request.user, tangle=daily_tangle_instance).exists():
            messages.error(request, "You have already submitted for today's tangle.")
            return HttpResponse(
                '<div class="p-4 text-red-600"><strong>Error:</strong> You have already submitted today.</div>',
                status=400
            )

    # Continue building board...
    num_rows = len(daily_tangle_instance.get_row_words())
    num_cols = len(daily_tangle_instance.get_column_words())
    board = []
    for row in range(1, num_rows + 1):
        row_data = []
        for col in range(1, num_cols + 1):
            cell = request.POST.get(f'word_{row}_{col}', '').upper()
            row_data.append(cell)
        board.append(row_data)

    # Validate board...
    errors = []
    for row_idx in range(num_rows):
        row_word = daily_tangle_instance.get_row_words()[row_idx].upper()
        for col_idx in range(num_cols):
            col_word = daily_tangle_instance.get_column_words()[col_idx].upper()
            letter = board[row_idx][col_idx]
            if letter and letter not in row_word and letter not in col_word:
                errors.append({
                    'cell': (row_idx + 1, col_idx + 1),
                    'letter': letter,
                    'row_word': row_word,
                    'col_word': col_word
                })

    if errors:
        error_html = '<ul class="list-disc pl-4">'
        for error in errors:
            error_html += (
                f'<li>Cell {error["cell"]}: '
                f'"{error["letter"]}" must be in row "{error["row_word"]}" '
                f'or column "{error["col_word"]}".</li>'
            )
        error_html += '</ul>'
        return HttpResponse(
            f'<div class="p-4 text-red-600">'
            f'<strong>Submission Errors:</strong>{error_html}</div>',
            status=400
        )

    # Valid submission
    score_breakdown, score_breakdown_numbers, definitions , words = process_valid_submissions(board)

    if request.user.is_authenticated:
        try:
            TangleAttempt.objects.create(
                user=request.user,
                tangle=daily_tangle_instance,
                words={
                    "word1": words[0],
                    "word1_points": score_breakdown_numbers[0],
                    "word2": words[1],
                    "word2_points": score_breakdown_numbers[1],
                    "word3": words[2],
                    "word3_points": score_breakdown_numbers[2],
                    "word4": words[3],
                    "word4_points": score_breakdown_numbers[3],
                    "total_score": sum(score_breakdown_numbers)
                },
                points=sum(score_breakdown_numbers)
            )
            request.user.totalTanglePointsEver += sum(score_breakdown_numbers)
            request.user.save()
        except IntegrityError:
            messages.error(request, "You have already submitted for today's tangle.")
            return HttpResponse(
                '<div class="p-4 text-red-600"><strong>Error:</strong> Duplicate submission detected.</div>',
                status=400
            )

    return render(request, 'pages/tangle/partials/results_modal.html', {
        'definitions': definitions,
        'score_breakdown': score_breakdown,
        'words': words,
        'attempted': True,
    })

    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.db.models import OuterRef, Subquery, Max, F

def tangleRankings(request):
    today = datetime.date.today()
    tangle = DailyTangle.objects.filter(date=today).first()
    filter_type = request.GET.get("filter", "daily")

    if filter_type == "alltime":
        # Get each user's best scoring attempt ever
        subquery = (
            TangleAttempt.objects
            .filter(user=OuterRef('user'))
            .order_by('-points', '-created_at')  # prioritize high score, then recency
        )
        users = (
            TangleAttempt.objects
            .select_related('user')
            .order_by('user', '-points', '-created_at')
            .distinct('user')
        )

    else:
        # Get best attempt per user for today's tangle
        subquery = (
            TangleAttempt.objects
            .filter(tangle=tangle, user=OuterRef('user'))
            .order_by('-points', '-created_at')
        )
        users = (
            TangleAttempt.objects
            .filter(tangle=tangle)
            .select_related('user')
            .order_by('user', '-points', '-created_at')
            .distinct('user')
        )

    table = {}
    for i, user in enumerate(users):
        table[i + 1] = {
            "username": user.user,
            "points": user.points,
            "totalTanglePoints": user.user.totalTanglePointsEver,
            "day": user.created_at.strftime("%Y-%m-%d"),
        }
    # Sort the table by points in descending order
    users = sorted(users, key=lambda u: u.points, reverse=True)

    # Create a paginator for the user scores
    paginator = Paginator(tuple(table.items()), 10)
    page_number = request.GET.get("page")
    user_scores = paginator.get_page(page_number)

    context = {
        "user_scores": user_scores,
        "tangle": tangle,
        "filter": filter_type,
    }

    if request.htmx:
        return render(request, "pages/tangle/partials/top10users.html", context)
    else:
        return render(request, "pages/tangle/fame.html", context)

