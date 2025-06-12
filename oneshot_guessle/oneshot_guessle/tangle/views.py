from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
import datetime
from django.conf import settings
from django.contrib.staticfiles.finders import find
from random import sample


# importing functions
from .functions.twl import check
from .models import DailyTangle, TangleAttempt

from .utils import process_valid_submissions
# Create your views here.



def tangle_index(request):
    """
    Renders the index page of the words game.
    This will create a a list of words for the day's tangle if one does not already exist.
    If a tangle already exists for today, it will retrieve the existing tangle.
    """
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

    # Safely define `words` before use
    words = {}
    attempted = False

    if request.user.is_authenticated:
        attempt = TangleAttempt.objects.filter(user=request.user, tangle=tangle).first()
        if attempt:
            attempted = True
            words = attempt.words

    previous_words = {
        "word1": words["word1"][0:5] if words else "",
        "word2": words["word2"][0:5] if words else "",
        "word3": words["word3"][0:5] if words else "",
        "word4": words["word4"][0:5] if words else "",    
        }
    previous_words_list = [list(word) for key, word in sorted(previous_words.items())]

    context = {
        'tangle': tangle,
        'attempted': attempted,
        'previous_words': previous_words_list,
    }
    return render(request, 'pages/tangle/tangle_index.html', context)


@require_POST
def submit_words(request):
    if request.method == 'POST':
        # 1️⃣ Fetch the tangle
        tangle_id = request.POST.get('tangle_id') or request.session.get('current_tangle_id')
        daily_tangle_instance = get_object_or_404(DailyTangle, id=tangle_id)

        # 2️⃣ Build the user's board
        num_rows = len(daily_tangle_instance.get_row_words())
        num_cols = len(daily_tangle_instance.get_column_words())
        board = []

        for row in range(1, num_rows + 1):
            row_data = []
            for col in range(1, num_cols + 1):
                cell = request.POST.get(f'word_{row}_{col}', '').upper()
                row_data.append(cell)
            board.append(row_data)
        # print("Board submitted:", board)
        # 3️⃣ Validate the board (check letters against rows and columns)
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
            # Build error HTML
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

        
        # 5️⃣ Process valid submissions
        score_breakdown, score_breakdown_numbers, definitions , words = process_valid_submissions(board)
        if request.user.is_authenticated:
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
                }
            )

        # 6️⃣ Instead of JSON, render partial HTML for modal content
        return render(request, 'pages/tangle/partials/results_modal.html', {
            'definitions': definitions,
            'score_breakdown': score_breakdown,
            'words': words,
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
