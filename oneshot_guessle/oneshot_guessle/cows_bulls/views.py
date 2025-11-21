from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from random import sample

from oneshot_guessle.tangle.utils import SCORE_NUMBERS
from oneshot_guessle.cows_bulls.models import DailyOCB, DailyOCBAttempt

def generate_clue(answer, correct_count, correct_position_count):
    digits_not_in_answer = [d for d in '0123456789' if d not in answer]
    clue = list(sample(digits_not_in_answer, 5))
    clue_indexes = list(range(5))

    for _ in range(correct_position_count):
        idx = clue_indexes.pop(0)
        clue[idx] = answer[idx]

    for _ in range(correct_count - correct_position_count):
        original_idx = clue_indexes.pop(0)
        digit = answer[original_idx]
        wrong_positions = [i for i in range(5) if i != original_idx and clue[i] not in answer]
        if wrong_positions:
            clue[wrong_positions[0]] = digit

    return ''.join(clue)

def calculate_cows_bulls(secret_number, guess):
    cows = 0
    bulls = 0

    secret_digits = list(secret_number)
    guess_digits = list(guess)

    for i in range(len(secret_digits) - 1, -1, -1):
        if guess_digits[i] == secret_digits[i]:
            bulls += 1
            secret_digits.pop(i)
            guess_digits.pop(i)

    for g_digit in guess_digits:
        if g_digit in secret_digits:
            cows += 1
            secret_digits.remove(g_digit)

    return cows, bulls

def cb_index(request):
    today = timezone.now().date()
    ocb = DailyOCB.objects.filter(date=today).first()

    if not ocb:
        ocb = create_daily_puzzle()

    clues = [
        (ocb.clue1, "0️⃣ 🐄 cows <br>0️⃣🐂 bulls"),
        (ocb.clue2, "1️⃣ cow 🐄"),
        (ocb.clue3, "1️⃣ bull 🐂"),
        (ocb.clue4, "2️⃣ cows 🐄"),
    ]

    if request.method == 'POST' and request.user.is_authenticated:
        return handle_guess_submission(request, ocb, clues)

    return handle_page_load(request, ocb, clues)

def create_daily_puzzle():
    number = ''.join(sample('0123456789', 5))
    return DailyOCB.objects.create(
        date=timezone.now().date(),
        number=number,
        clue1=''.join(sample([d for d in '0123456789' if d not in number], 5)),
        clue2=generate_clue(number, 1, 0),
        clue3=generate_clue(number, 1, 1),
        clue4=generate_clue(number, 2, 0)
    )

def handle_guess_submission(request, ocb, base_clues):
    guess = ''.join(request.POST.get(f'digit{i}', '') for i in range(1, 6))

    if len(guess) != 5 or not guess.isdigit():
        messages.error(request, "Please enter a valid 5-digit number.")
        return HttpResponse(status=400)

    attempts = DailyOCBAttempt.objects.filter(user=request.user, ocb=ocb).order_by('timestamp')

    winning_attempt = attempts.filter(bulls=5).first()
    if winning_attempt:
        messages.warning(request, f"You've already solved today's puzzle in {winning_attempt.attempt_number} attempts!")
        return HttpResponse(status=200)

    attempt_number = attempts.count() + 1
    cows, bulls = calculate_cows_bulls(ocb.number, guess)

    DailyOCBAttempt.objects.create(
        user=request.user,
        ocb=ocb,
        guess=guess,
        cows=cows,
        bulls=bulls,
        attempt_number=attempt_number
    )

    update_user_stats(request.user, attempt_number, bulls == 5)
    create_response_messages(request, ocb.number, guess, cows, bulls, attempt_number)

    attempts = DailyOCBAttempt.objects.filter(user=request.user, ocb=ocb).order_by('timestamp')
    clues = build_clues_list(ocb, attempts)

    clues_html = render_to_string('pages/cows_bulls/partials/_clues_table_body.html', {
        'clues': clues,
        'is_solved_today': bulls == 5,
        'ocb': ocb,
        'attempt_number': attempt_number,
        'messages': messages.get_messages(request),
    })

    response = HttpResponse(clues_html)
    response['HX-Trigger'] = 'newAttempt'
    if bulls == 5:
        response['HX-Trigger'] += ',puzzleSolved'

    return response

def handle_page_load(request, ocb, base_clues):
    attempts = []
    attempted_today = False
    is_solved_today = False

    if request.user.is_authenticated:
        attempts = DailyOCBAttempt.objects.filter(user=request.user, ocb=ocb).order_by('timestamp')
        if attempts.exists():
            attempted_today = True
            is_solved_today = attempts.filter(bulls=5).exists()

    clues = build_clues_list(ocb, attempts) if attempts else base_clues

    context = {
        'ocb': ocb,
        'clues': clues,
        'attempted': attempted_today,
        'is_solved_today': is_solved_today,
        'today': ocb.date,
        'messages': messages.get_messages(request),
    }

    if is_solved_today:
        winning_attempt = attempts.filter(bulls=5).first()
        if winning_attempt:
            context['attempt_number'] = winning_attempt.attempt_number

    return render(request, 'pages/cows_bulls/cb_index.html', context)

def update_user_stats(user, attempt_number, is_solved):
    if not user.cows_bulls_attempts:
        user.cows_bulls_attempts = 0
    user.cows_bulls_attempts += 1

    if is_solved:
        points_awarded = max(0, 6 - attempt_number)
        user.cows_bulls_points += points_awarded
    user.save()

def create_response_messages(request, puzzle_number, guess, cows, bulls, attempt_number):
    if bulls == 5:
        messages.success(request,
            f"🎉 You cracked the code {puzzle_number} in {attempt_number} tries! (+{max(0, 6 - attempt_number)} points)")
    else:
        messages.info(request,
            f"Your guess {guess}: {SCORE_NUMBERS[cows]} {'cow' if cows==1 else 'cows'} 🐄<br>"
            f"{SCORE_NUMBERS[bulls]} {'bull' if bulls==1 else 'bulls'} 🐂.")

def build_clues_list(ocb_instance, attempts_queryset):
    clues = [
        (ocb_instance.clue1, "0️⃣ 🐄 cows <br>0️⃣🐂 bulls"),
        (ocb_instance.clue2, "1️⃣ cow 🐄"),
        (ocb_instance.clue3, "1️⃣ bull 🐂"),
        (ocb_instance.clue4, "2️⃣ cows 🐄"),
    ]

    for att in attempts_queryset:
        clues.append((att.guess, f'{SCORE_NUMBERS[att.cows]} {"cow" if att.cows==1 else "cows"} 🐄<br>'
                                 f'{SCORE_NUMBERS[att.bulls]} {"bull" if att.bulls==1 else "bulls"} 🐂'))

    return clues
