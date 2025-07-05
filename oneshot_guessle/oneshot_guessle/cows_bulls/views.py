from django.shortcuts import render, redirect
from django.utils import timezone
from random import sample
from django.contrib import messages
from django.db import transaction

from oneshot_guessle.tangle.utils import SCORE_NUMBERS

# from oneshot_guessle.cows_bulls.models import DailyOCB
from oneshot_guessle.cows_bulls.models import DailyOCB, DailyOCBAttempt

# Create your views here.

def generate_clue(answer, correct_count, correct_position_count):
    digits_not_in_answer = [d for d in '0123456789' if d not in answer]
    clue = list(sample(digits_not_in_answer, 5)) # Start clue with wrong digits
    clue_indexes = list(range(5))

    # Add digits that are correct and in the correct place
    for _ in range(correct_position_count):
        idx = clue_indexes.pop(0)
        clue[idx] = answer[idx]

    # Add digits that are correct but in the wrong place
    for _ in range(correct_count - correct_position_count):
        original_idx = clue_indexes.pop(0)
        digit = answer[original_idx]
        wrong_positions = [i for i in range(5) if i != original_idx and clue[i] not in answer]
        if wrong_positions:
            clue[wrong_positions[0]] = digit
            return ''.join(clue)

def calculate_cows_bulls(secret_number, guess):
    """
    Calculates the number of 'cows' (correct digit, wrong position)
    and 'bulls' (correct digit, correct position) for a given guess
    against a secret number.

    Args:
    secret_number (str): The secret 5-digit number.
    guess (str): The 5-digit guess made by the user.

    Returns:
    tuple: A tuple containing (cows, bulls).
    """

    cows = 0
    bulls = 0

    # Create temporary copies or frequency maps for easier checking
    secret_digits = list(secret_number)
    guess_digits = list(guess)

    # Calculate Bulls first (correct digit, correct position)
    # Iterate backwards to safely remove elements
    for i in range(len(secret_digits) - 1, -1, -1):
        if guess_digits[i] == secret_digits[i]:

            bulls += 1
            # Remove matching digits to avoid double-counting as cows
            secret_digits.pop(i)
            guess_digits.pop(i)

    # Calculate Cows (correct digit, wrong position)
    # Now, iterate through remaining guess digits and check against remaining secret digits
    for g_digit in guess_digits:
        if g_digit in secret_digits:
            cows += 1
            secret_digits.remove(g_digit) # Remove to avoid double-counting if guess has duplicates

    return cows, bulls

def cb_index(request):

    today = timezone.now().date()
    ocb = DailyOCB.objects.filter(date=today).first()

    # Create new puzzle if none exists for today
    if not ocb:
        ocb = create_daily_puzzle()

    # Initialize base clues
    clues = [
        (ocb.clue1, "0️⃣ 🐄 cows <br>0️⃣🐂 bulls"),
        (ocb.clue2, "1️⃣ cow 🐄"),
        (ocb.clue3, "1️⃣ bull 🐂"),
        (ocb.clue4, "2️⃣ cows 🐄"),
    ]

    # Handle POST requests (form submissions)
    if request.method == 'POST' and request.user.is_authenticated:
        return handle_guess_submission(request, ocb, clues)

    # Handle GET requests (initial page load)
    return handle_page_load(request, ocb, clues)



def create_daily_puzzle():
    """Create a new daily puzzle"""
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
    """Process user's guess submission"""
    guess = ''.join(request.POST.get(f'digit{i}', '') for i in range(1, 6))
    
    # Validate input
    if len(guess) != 5 or not guess.isdigit():
        messages.error(request, "Please enter a valid 5-digit number.")
        return render(request, 'pages/cows_bulls/partials/_messages.html', {
            'messages': messages.get_messages(request)
        })

    attempts = DailyOCBAttempt.objects.filter(
        user=request.user,
        ocb=ocb
    ).order_by('timestamp')

    # Check if already solved
    winning_attempt = attempts.filter(bulls=5).first()
    if winning_attempt:       
        messages.warning(request,
            f"You've already solved today's puzzle in {winning_attempt.attempt_number} attempts!"
        )
        return render(request, 'pages/cows_bulls/partials/_messages.html', {
            'messages': messages.get_messages(request)
            })

    # Process new attempt
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

    # Update user stats and messages
    update_user_stats(request.user, attempt_number, bulls == 5)
    create_response_messages(request, ocb.number, guess, cows, bulls, attempt_number)

    # Prepare response
    attempts = DailyOCBAttempt.objects.filter(user=request.user, ocb=ocb).order_by('timestamp')
    clues = build_clues_list(ocb, attempts)

    response = render(request, 'pages/cows_bulls/partials/_clues_table_body.html', {
        'clues': clues,
        'is_solved_today': bulls == 5,
        'ocb': ocb,
        'attempt_number': attempt_number,
        'messages': messages.get_messages(request), # Include messages for HTMX
    })

    response['HX-Trigger'] = 'puzzleSolved'
    response['HX-Trigger-After-Swap'] = 'newAttempt'
    return response


def handle_page_load(request, ocb, base_clues):

    """Handle initial page load"""
    attempts = []
    attempted_today = False
    is_solved_today = False
    if request.user.is_authenticated:
        attempts = DailyOCBAttempt.objects.filter(
            user=request.user,
            ocb=ocb
        ).order_by('timestamp')

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

    """Update user statistics"""
    if not user.cows_bulls_attempts:
        user.cows_bulls_attempts = 0
        user.cows_bulls_attempts += 1

    if is_solved:
        points_awarded = max(0, 6 - attempt_number)
        user.cows_bulls_points += points_awarded
        user.save()

def create_response_messages(request, puzzle_number, guess, cows, bulls, attempt_number):

    """Create appropriate response messages"""

    if bulls == 5:
        messages.success(request,
            f"🎉 You cracked the code {puzzle_number} in {attempt_number} tries! "
            f"(+{max(0, 6 - attempt_number)} points)"
        )
    else:
        messages.info(request,
            f"Your guess {guess}: {SCORE_NUMBERS[cows]} "
            f"{'cow' if cows==1 else 'cows'}🐄 {SCORE_NUMBERS[bulls]} "
            f"{'bull' if bulls==1 else 'bulls'}🐂."
        )

# Helper function to build the clues list (avoids code duplication)
def build_clues_list(ocb_instance, attempts_queryset):
    """
    Builds the combined list of initial clues and user's past attempts.
    """

    clues = [
        (ocb_instance.clue1, "0️⃣ 🐄 cows <br>0️⃣🐂 bulls"),
        (ocb_instance.clue2, "1️⃣ cow 🐄"),
        (ocb_instance.clue3, "1️⃣ bull 🐂"),
        (ocb_instance.clue4, "2️⃣ cows 🐄"),
    ]

    for att in attempts_queryset:
        clues.append((att.guess, f'{SCORE_NUMBERS[att.cows]} {"cow" if att.cows==1 else "cows"} 🐄<br>{SCORE_NUMBERS[att.bulls]} {"bull" if att.bulls==1 else "bulls"} 🐂'))

    return clues