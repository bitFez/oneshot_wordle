from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Subquery, OuterRef
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

User = get_user_model()

from django.core.mail import send_mail

from .forms import GuessleForm, GuessForm, GuessleFormHard, GuessFormHard, AlphabetForm
from .models import *
from .functions import guess_result, get_random_clues, get_clues_rows, check_plural
# from .forms import MessageForm

ENCODING_FORMAT='utf8' 

# Create your views here.
def serve_ads_txt(request):
  return HttpResponse("google.com, pub-2072226965226950, DIRECT, f08c47fec0942fa0")

def load_words(request):
    # opening JSON words file
    # file_ = staticfiles_storage.url('dicts/words.json') #static('dicts/words.json')
    if settings.DEBUG:
        file_ = find('dicts/words.txt')
        with open(file_) as f:
            data =f.readlines()
    else:
        # file_ = staticfiles_storage.url('dicts/words.txt')
        with open(r'oneshot_guessle/game/dicts/words.txt') as f:
            data =f.readlines()
    # storage = ManifestStaticFilesStorage()
    # with storage.open(file_, "r") as f:
    # with open(r'oneshot_guessle/game/words.txt') as f:
    #     data =f.read()
    # data = f.readlines() # json.load(f)

    newWords = 0
    lenOfData = len(data)
    for item in range(0, len(data)):
        wd = data[item].rstrip('\n')  
        if not Word.objects.filter(word=wd).exists():
            obj = Word.objects.update_or_create(
                word = wd
            )
            newWords += 1
        print(f"Adding 5 Letter Words: {wd}: {round((item/lenOfData)*100,2)}%")
    
    if settings.DEBUG:
        file_ = find('dicts/6-letter-words.txt')
        with open(file_, 'r', encoding='utf8') as f:
            data =f.read().splitlines()
    else:
        with open(r'oneshot_guessle/game/dicts/6-letter-words.txt') as f:
            data = [line.rstrip('\n') for line in f]
    
    new6Words = 0
    lenOfData = len(data)
    for item in range(0, len(data)):
        wd = data[item].rstrip('\n')  
        if not WordsHard.objects.filter(word=wd).exists():
            obj = WordsHard.objects.update_or_create(
                word = wd
            )
            new6Words += 1
        print(f"Adding 6 Letter Words {round((item/lenOfData)*100,2)}%")
    msg = f"Added {newWords} new 5 letter words and {new6Words} new 6 letter words."
    context = {'msg':msg}
    return render(request, 'pages/games/words_loaded.html', context)


def get_random_word(**kwargs):
    difficulty = kwargs.get('difficulty', None)
    cutoff = datetime.now() - timedelta(days=730)
    Model = WordsHard if difficulty == "hard" else Word
    base_qs = Model.objects.filter(
        Q(lastOccurance__lte=cutoff) | Q(frequency=0),
        proper_noun=False,  # exclude proper nouns for target word
    )
    # Try a few random candidates and use check_plural to avoid plurals.
    for _ in range(10):
        candidate = base_qs.order_by('?').first()
        if not candidate:
            break
        word_text = getattr(candidate, "word", str(candidate))
        try:
            if not check_plural(word_text):
                return candidate
        except Exception:
            # if the plural check fails for any reason, skip this candidate
            continue

    # Fallback: scan through the queryset for the first non-plural
    for candidate in base_qs:
        word_text = getattr(candidate, "word", str(candidate))
        try:
            if not check_plural(word_text):
                return candidate
        except Exception:
            continue

    # Last resort: return any random word (may be plural/proper)
    return Model.objects.order_by('?').first()

def scan_for_plurals(request, **kwargs):
    difficulty = kwargs.get('diff', None)
    if difficulty == "hard":
        # return WordsHard.objects.filter(Q(lastOccurance__lte=datetime.now() - timedelta(days=730)) | Q(frequency=0)).order_by('?')[0]
        words = WordsHard.objects.all()
        for word in words:
            a = WordsHard.objects.get(word = word)
            if check_plural(word.word) == True:
                a.proper_noun = False
                a.save()
            else:
                a.proper_noun = True
                a.save()
    elif difficulty == "easy":
        words = Word.objects.all()
        for word in words:
            print(f"---> word is: {word}")
            a = Word.objects.get(word = word)
            if check_plural(word.word) == True:
                a.proper_noun = False
                a.save()
            else:
                a.proper_noun = True
                a.save()
    else:
        pass
    return HttpResponse("Scanned for plurals and updated the database accordingly. Please check the admin panel to confirm.")

def _get_daily_stars_for_date(user, today_dt):
    """
    Return the single Daily_Stars row for `user` for the calendar date of today_dt.
    Create it if missing. Use date__date to match by day (avoids duplicate rows).
    """
    # ensure we compare by date
    today_date = today_dt.date()
    stars = Daily_Stars.objects.filter(user=user, date__date=today_date).first()
    if stars is None:
        # create a new row; date field has auto_now so it will be set on save
        stars = Daily_Stars.objects.create(user=user, stars=0)
    return stars

def guessle(request):   
    #initiate array for alphabet colors
    AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
    alphabet_formset = AlphabetFormSet(form_kwargs={'empty_permitted': False}, prefix='alphabet')
    #initiate formset for guesslist
    GuessFormSet = formset_factory(GuessForm, extra=1, max_num=1)

    context = {}
    # ensure these exist for anonymous users so later code can safely call .exists()/first()
    attempts = Guessle_Attempt.objects.none()
    stars = None

    # Get today's todays date
    today_dt = timezone.localtime(timezone.now())
    # Get current datetime and its date for daily lookups
    today_dt = timezone.localtime(timezone.now())
    today = today_dt  # keep variable name used elsewhere for created datetimes
    today_date = today_dt.date()

    if request.user.is_authenticated:
        #get user
        user = get_object_or_404(User, pk=request.user.id)
        # Get or create the single Daily_Stars record for this calendar day
        stars = _get_daily_stars_for_date(user, today_dt)
        context['stars'] = stars
        # Check for previous attempts by calendar date
        attempts = Guessle_Attempt.objects.filter(date__date=today_date, user=user).order_by('-date')
        # add numeric count for templates/JS to use (always present)
        context['attempts_count'] = attempts.count() if attempts is not None else 0

    # query if a word has been created already today in the DB.
    if OneshotWord.objects.filter(date__date=today_date).exists():
        todaysGuessle = OneshotWord.objects.filter(date__date=today_date).first()
        todaysword = todaysGuessle
        todayclues = getattr(todaysGuessle, "clues", None)
        TARGET_WORD = todaysGuessle.word
        # ensure TARGET_WORD is a string (Word may be a model instance)
        if hasattr(TARGET_WORD, "word"):
            TARGET_WORD = TARGET_WORD.word
        elif not isinstance(TARGET_WORD, str):
            TARGET_WORD = str(TARGET_WORD)
        
        # coerce clue fields to plain strings (handle Word model instances)
        def _clue_text(c):
            if c is None:
                return ""
            if hasattr(c, "word"):
                return c.word
            return str(c)

        clues = [
            _clue_text(getattr(todayclues, "clue1", None)),
            _clue_text(getattr(todayclues, "clue2", None)),
            _clue_text(getattr(todayclues, "clue3", None)),
            _clue_text(getattr(todayclues, "clue4", None)),
            _clue_text(getattr(todayclues, "clue5", None)),
        ]
    else:
        # get a new word for today if one doesn't exist
        todaysword = get_random_word()
        # get todays random clues
        clue_texts = get_random_clues(todaysword.word, difficulty="regular")
        # Debug + normalize: ensure we have a list of full-word strings
        # print("DEBUG get_random_clues returned (type):", type(clue_texts), "repr:", repr(clue_texts))
        if isinstance(clue_texts, str):
            # defensive: if a string was returned, wrap into list (string indexed -> single chars bug)
            # prefer to split on whitespace if that is a possible format, else treat as single word
            if " " in clue_texts:
                clue_texts = clue_texts.split()
            else:
                clue_texts = [clue_texts]
        # ensure list length >=5: if not, expand with fallback (fetch from DB)
        if not isinstance(clue_texts, (list, tuple)) or len(clue_texts) < 5:
            qs = WordsHard.objects if False else Word.objects  # regular -> Word
            fallback = []
            for cand in qs.filter():  # simplest fallback
                w = str(getattr(cand, "word", cand)).lower()
                if w != str(todaysword.word).lower() and len(w) == len(str(todaysword.word)):
                    fallback.append(w)
                    if len(fallback) == 5:
                        break
            # merge keeping existing items first
            clue_texts = list(clue_texts) + [c for c in fallback if c not in clue_texts]
        # final trim/pad to length 5
        clue_texts = (clue_texts + [""]*5)[:5]
 
        clues_obj, _ = OneshotClues.objects.update_or_create(
            clue1 = clue_texts[0],
            clue2 = clue_texts[1],
            clue3 = clue_texts[2],
            clue4 = clue_texts[3],
            clue5 = clue_texts[4]
        )
        oneshot_obj, _ = OneshotWord.objects.update_or_create(
            word=todaysword.word,
            defaults={"clues": clues_obj, "date": today},
        )
        # use the created oneshot as today's guessle
        todaysGuessle = oneshot_obj
        todayclues = clues_obj
        TARGET_WORD = todaysGuessle.word
        if hasattr(TARGET_WORD, "word"):
            TARGET_WORD = TARGET_WORD.word
        elif not isinstance(TARGET_WORD, str):
            TARGET_WORD = str(TARGET_WORD)
        
        # coerce clue fields to plain strings (handle Word model instances)
        def _clue_text(c):
            if c is None:
                return ""
            if hasattr(c, "word"):
                return c.word
            return str(c)

        clues = [
            _clue_text(getattr(todayclues, "clue1", None)),
            _clue_text(getattr(todayclues, "clue2", None)),
            _clue_text(getattr(todayclues, "clue3", None)),
            _clue_text(getattr(todayclues, "clue4", None)),
            _clue_text(getattr(todayclues, "clue5", None)),
        ]
        # increment frequency on the todaysword instance if present
        try:
            todaysword.frequency = (todaysword.frequency or 0) + 1
            todaysword.save()
        except Exception:
            pass

    # This section will add each clue to the guessle rows with the correct colour for each letter.
    cluesRow,alphabet = get_clues_rows(clues, TARGET_WORD)

    # ensure target word is always present in context (needed by client JS)
    context['t_word'] = str(TARGET_WORD or "")
    
    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.data,prefix='alphabet')
    context['alphabet_formset'] = new_alphabet_formset
    context['cluesRow'] = cluesRow
    context['guessleNo'] = todaysGuessle.id
    context['coloured_alpha'] = alphabet
    
    # Dealing with the post of a guess
    if request.method == 'POST':

        #load the 5-words scrabble dictionary
        if settings.DEBUG:
            five_letter_words = find('dicts/5-letter-words.json')
        else:
            five_letter_words = find('dicts/5-letter-words.json')
            # five_letter_words = open(r'oneshot_guessle/game/dicts/5-letter-words.json')
        en_dict = json.load(open(five_letter_words))
        en_list = [en['word'] for en in en_dict]

        #initiate array for alphabet colors
        AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
        
        #initiate formset for guesslist
        GuessFormSet = formset_factory(GuessForm, extra=1, max_num=1)
        #read the forms from copy of request.POST to make them mutable
        guess_formset = GuessFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='guess')
        alphabet_formset = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='alphabet')
        form = GuessleForm(request.POST.copy())

        if guess_formset.is_valid() & form.is_valid() & alphabet_formset.is_valid():
            
            # Get form data
            guess = form.cleaned_data['guess'].lower()
            attempts_left = form.cleaned_data['attempts_left']
            attempt_number = form.cleaned_data['attempt_number']
            
            #check if entered word is in dictionary
            if guess in en_list:
                #valid attempt to increment
                form.data['attempt_number'] = attempt_number+ 1
                form.data['attempts_left'] = attempts_left - 1

                #get the latest word
                guess_form = guess_formset[attempt_number-1]
                guess_form.cleaned_data['guess'] = guess
                
                # Display the result of the guess
                row,alphabet=guess_result(guess, TARGET_WORD, alphabet)     
                cluesRow.append(row)   
                # new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                context['form'] = form
                # context['guess_formset'] = new_guess_formset
                context['alphabet_formset'] = new_alphabet_formset
                context['cluesRow'] = cluesRow

            if not request.user.is_authenticated:
                if guess == TARGET_WORD:
                    messages.add_message(request=request, level=messages.SUCCESS, message='You Guessled in one Shot!!'+'<br>'+'But why not sign up to save your progress and try daily Easy or hard challenge?'+'<br>'+'Also, why not challenge your friends too? ')
                elif attempts_left == 1:
                    messages.add_message(request=request, level=messages.ERROR, message = 'Wrong answer! The actual word is '+TARGET_WORD +'. <br>'+'But why not sign up to save your progress and try daily Easy or hard challenge?'+'<br>'+'Also, why not challenge your friends too? ')
                else:
                    messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                    context['guess_formset'] = guess_formset
                    context['form'] = form
                    context['alphabet_formset'] = alphabet_formset

            else:
                #get user
                user = get_object_or_404(User, pk=request.user.id)
                
                # Add stats if the user is logged in
                if guess == TARGET_WORD:
                    messages.add_message(request=request, level=messages.SUCCESS, message='You Guessled in one Shot!!'+'<br>'+'Have you tried the daily Easy or hard challenge?'+'<br>'+'Also, why not challenge your friends too? ')
                    todaysGuessle.attempts+=1
                    todaysGuessle.correctAnswers+=1
                    todaysGuessle.save()
                    stars.stars += 1
                    user.stars += 1
                    stars.save()
                    
                    user.dayscorrect+=1
                    # check for attempt yesterday
                    yesterday_date = (today_dt - timedelta(days=1)).date()
                    yesterday_qs = Guessle_Attempt.objects.filter(date__date=yesterday_date, user=user)
                    if yesterday_qs.exists():
                        yesterday_attempt = yesterday_qs.first()
                        # check yesterday's word against the attempt
                        prev_word = getattr(yesterday_attempt.word, "word", yesterday_attempt.word)
                        if str(yesterday_attempt.guess) == str(prev_word):
                            user.streak = (user.streak or 0) + 1
                            if user.streak > (user.highestStreak or 0):
                                user.highestStreak = user.streak
                        else:
                            user.streak = 0
                    
                    # if an attempt doesnt exist for yesterday, streak = 0
                    else:
                        user.streak = 0
                    
                    context['stars'] = stars
                    
                    
                elif attempts_left == 1:
                    messages.add_message(request=request, level=messages.ERROR, message = 'Chances are over. word is '+TARGET_WORD)
                    todaysGuessle.attempts+=1
                    todaysGuessle.save()
                    user.daysincorrect+=1
                    user.streak = 0
                
                att = Guessle_Attempt.objects.update_or_create(
                        user=user,
                        date=today,
                        word=todaysGuessle,
                        guess=guess
                    )
                user.save()
        else:
            messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
            context['guess_formset'] = guess_formset
            context['form'] = form
            context['alphabet_formset'] = alphabet_formset

            print(form.errors)
            print(form.non_field_errors)
            print(guess_formset.errors)
            print(guess_formset.non_form_errors())
            print(alphabet_formset.errors)
            print(alphabet_formset.non_form_errors())
    
    
    else:
        # not a POST: if the user already attempted today show their attempt and coloured result
        previous_attempt = attempts.first() if attempts.exists() else None
        if previous_attempt:
            # show message and populate the form with the previous guess (readonly behaviour)
            messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's Guessle")
            # pre-fill form with the user's previous guess and zero attempts left
            form = GuessleForm(initial={
                'guess':previous_attempt.guess,
                'attempts_left':0,
                'attempt_number': 0,
            })
            attempt_number = 0
            # compute coloured row & alphabet from the previous guess
            row, alphabet = guess_result(previous_attempt.guess, TARGET_WORD, alphabet)
            cluesRow.append(row)
            context['cluesRow'] = cluesRow
            context['attempts'] = attempts
            # prepare small readonly formsets (keeps template expectation of formsets)
            guess_formset = GuessFormSet(prefix='guess')
            alphabet_formset = AlphabetFormSet(prefix='alphabet')
            context['form'] = form
            context['guess_formset'] = guess_formset
            context['alphabet_formset'] = alphabet_formset
            # render immediately so we don't override the form below
            if request.user.is_authenticated:
                user.save()
            return render(request, 'pages/games/guessle.html', context)
            
        # if no previous attempts: prepare a fresh form for the user
        attempt_number = 1
        form = GuessleForm(initial={})
        form.fields['attempts_left'].initial= 1
        form.fields['attempt_number'].initial = 1
        guess_formset = GuessFormSet(prefix='guess')
        alphabet_formset = AlphabetFormSet(prefix='alphabet')
        guess_form = guess_formset[attempt_number-1]

        i=1
        for guess_form in guess_formset:
            x_ref = 'guess_'+str(i)
            guess_form.fields['guess'].widget.attrs.update({'x-ref':x_ref,'x-model':x_ref+'_xmodel'})
            i=i+1

        #initiate the variables to send to the template
        context['form'] = form
        context['guess_formset'] = guess_formset
        context['alphabet_formset'] = alphabet_formset
   
    context['t_word'] = TARGET_WORD
        

    #send back the html template
    return render(request, 'pages/games/guessle.html', context)

@login_required(login_url="/accounts/login/")
def guessle_easy(request):
    #get user
    user = get_object_or_404(User, pk=request.user.id)
    
    #initiate array for alphabet colors
    AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
    alphabet_formset = AlphabetFormSet(form_kwargs={'empty_permitted': False}, prefix='alphabet')
    #initiate formset for guesslist
    GuessFormSet = formset_factory(GuessForm, extra=1, max_num=1)

    context = {}
    # Get today's todays date
    today_dt = timezone.localtime(timezone.now())
    today = today_dt 
    today_date = today_dt.date()
    
    # Check for number of daily stars
    stars = _get_daily_stars_for_date(user, today_dt)
    # Check for previous attempts
    attempts = EasyGuessle_Attempt.objects.filter(date__date=today_date, user=user).order_by('-date')
    
    # add numeric count for templates/JS to use (always present)
    context['attempts_count'] = attempts.count() if attempts is not None else 0

    # query if a word has been created already today in the DB.
    if OneshotWordEasy.objects.filter(date__date=today_date).exists():
        todaysGuessle = OneshotWordEasy.objects.filter(date__date=today_date)[0] 
        todaysword = todaysGuessle
        todayclues = getattr(todaysGuessle, "clues", None)
        TARGET_WORD = todaysGuessle.word
        # ensure TARGET_WORD is a string (Word may be a model instance)
        if hasattr(TARGET_WORD, "word"):
            TARGET_WORD = TARGET_WORD.word
        elif not isinstance(TARGET_WORD, str):
            TARGET_WORD = str(TARGET_WORD)
        
        # coerce clue fields to plain strings (handle Word model instances)
        def _clue_text(c):
            if c is None:
                return ""
            if hasattr(c, "word"):
                return c.word
            return str(c)

        clues = [
            _clue_text(getattr(todayclues, "clue1", None)),
            _clue_text(getattr(todayclues, "clue2", None)),
            _clue_text(getattr(todayclues, "clue3", None)),
            _clue_text(getattr(todayclues, "clue4", None)),
            _clue_text(getattr(todayclues, "clue5", None)),
        ]
    else:
        # get a new word for today if one doesn't exist
        todaysword = get_random_word()
        # get todays random clues
        clue_texts = get_random_clues(todaysword.word, difficulty="easy")
        # Debug + normalize: ensure we have a list of full-word strings
        # print("DEBUG get_random_clues returned (type):", type(clue_texts), "repr:", repr(clue_texts))
        if isinstance(clue_texts, str):
            # defensive: if a string was returned, wrap into list (string indexed -> single chars bug)
            # prefer to split on whitespace if that is a possible format, else treat as single word
            if " " in clue_texts:
                clue_texts = clue_texts.split()
            else:
                clue_texts = [clue_texts]
        # ensure list length >=5: if not, expand with fallback (fetch from DB)
        if not isinstance(clue_texts, (list, tuple)) or len(clue_texts) < 5:
            qs = WordsHard.objects if False else Word.objects  # regular -> Word
            fallback = []
            for cand in qs.filter():  # simplest fallback
                w = str(getattr(cand, "word", cand)).lower()
                if w != str(todaysword.word).lower() and len(w) == len(str(todaysword.word)):
                    fallback.append(w)
                    if len(fallback) == 5:
                        break
            # merge keeping existing items first
            clue_texts = list(clue_texts) + [c for c in fallback if c not in clue_texts]
        # final trim/pad to length 5
        clue_texts = (clue_texts + [""]*5)[:5]
 
        clues_obj, _ = OneshotCluesEasy.objects.update_or_create(
            clue1 = clue_texts[0],
            clue2 = clue_texts[1],
            clue3 = clue_texts[2],
            clue4 = clue_texts[3],
            clue5 = clue_texts[4]
        )
        oneshot_obj, _ = OneshotWordEasy.objects.update_or_create(
            word=todaysword.word,
            defaults={"clues": clues_obj, "date": today},
        )
        # use the created oneshot as today's guessle
        todaysGuessle = oneshot_obj
        todayclues = clues_obj
        TARGET_WORD = todaysGuessle.word
        if hasattr(TARGET_WORD, "word"):
            TARGET_WORD = TARGET_WORD.word
        elif not isinstance(TARGET_WORD, str):
            TARGET_WORD = str(TARGET_WORD)
            
        # build plain-string clues list
        def _clue_text(c):
            if c is None:
                return ""
            if hasattr(c, "word"):
                return c.word
            return str(c)

        clues = [
            _clue_text(getattr(todayclues, "clue1", None)),
            _clue_text(getattr(todayclues, "clue2", None)),
            _clue_text(getattr(todayclues, "clue3", None)),
            _clue_text(getattr(todayclues, "clue4", None)),
            _clue_text(getattr(todayclues, "clue5", None)),
        ]
        # increment frequency on the todaysword instance if present
        try:
            todaysword.frequency = (todaysword.frequency or 0) + 1
            todaysword.save()
        except Exception:
            pass
                
    # This section will add each clue to the guessle rows with the correct colour for each letter.
    cluesRow,alphabet = get_clues_rows(clues, TARGET_WORD, difficulty="easy")
    
    # ensure target word is always present in context (needed by client JS)
    context['t_word'] = str(TARGET_WORD or "")
    
    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.data,prefix='alphabet')
    context['alphabet_formset'] = new_alphabet_formset
    context['cluesRow'] = cluesRow
    context['guessleNo'] = todaysGuessle.id
    context['coloured_alpha'] = alphabet
    context['stars'] = stars
    context['difficulty'] = 'easy'
    
    # Dealing with the post of a guess
    if request.method == 'POST':   
        
        #load the 5-words scrabble dictionary
        if settings.DEBUG:
            five_letter_words = find('dicts/5-letter-words.json')
        else:
            five_letter_words = find('dicts/5-letter-words.json')
            # five_letter_words = static("r'oneshot_guessle/game/dicts/5-letter-words.json")
        en_dict = json.load(open(five_letter_words))
        en_list = [en['word'] for en in en_dict]

        #initiate array for alphabet colors
        AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
        
        #initiate formset for guesslist
        GuessFormSet = formset_factory(GuessForm, extra=1, max_num=1)
        #read the forms from copy of request.POST to make them mutable
        guess_formset = GuessFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='guess')
        alphabet_formset = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='alphabet')
        form = GuessleForm(request.POST.copy())

        if guess_formset.is_valid() & form.is_valid() & alphabet_formset.is_valid():
            
            # Get form data
            guess = form.cleaned_data['guess'].lower()
            attempts_left = form.cleaned_data['attempts_left']
            attempt_number = form.cleaned_data['attempt_number']
            
            #check if entered word is in dictionary
            if guess in en_list:
                #valid attempt to increment
                form.data['attempt_number'] = attempt_number+ 1
                form.data['attempts_left'] = attempts_left - 1

                #get the latest word
                guess_form = guess_formset[attempt_number-1]
                guess_form.cleaned_data['guess'] = guess
                
                # Display the result of the guess
                row, alphabet=guess_result(guess, TARGET_WORD, alphabet)     
                cluesRow.append(row)   
                # new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                context['form'] = form
                context['alphabet_formset'] = new_alphabet_formset
                context['cluesRow'] = cluesRow

                if guess == TARGET_WORD:
                    messages.add_message(request=request, level=messages.SUCCESS, message='You Guessled in one Shot!! Challenge your friend by clicking ')
                    todaysGuessle.attempts+=1
                    todaysGuessle.correctAnswers+=1
                    todaysGuessle.save()
                    stars.stars += 1
                    user.stars += 1
                    stars.save()
                    context['stars'] = stars
                elif attempts_left == 1:
                    messages.add_message(request=request, level=messages.ERROR, message = 'Chances are over. word is '+ TARGET_WORD)
                    todaysGuessle.attempts+=1
                    todaysGuessle.save()
                
                att = EasyGuessle_Attempt.objects.update_or_create(
                        user=user,
                        date=today,
                        word=todaysGuessle,
                        guess=guess
                    )
            else:
                messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                context['guess_formset'] = guess_formset
                context['form'] = form
                context['alphabet_formset'] = alphabet_formset

        else:
            print(form.errors)
            print(form.non_field_errors)
            print(guess_formset.errors)
            print(guess_formset.non_form_errors())
            print(alphabet_formset.errors)
            print(alphabet_formset.non_form_errors())
    
    
    else:
        # not a POST: if the user already attempted today show their attempt and coloured result
        previous_attempt = attempts.first() if attempts.exists() else None
        if previous_attempt:
            # show message and populate the form with the previous guess (readonly behaviour)
            messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's easy Guessle")
            # pre-fill form with the user's previous guess and zero attempts left
            form = GuessleForm(initial={
                'guess':previous_attempt.guess,
                'attempts_left':0,
                'attempt_number': 0,
            })
            attempt_number = 0
            # compute coloured row & alphabet from the previous guess
            row, alphabet = guess_result(previous_attempt.guess, TARGET_WORD, alphabet)
            cluesRow.append(row)
            context['cluesRow'] = cluesRow
            context['attempts'] = attempts
            # prepare small readonly formsets (keeps template expectation of formsets)
            guess_formset = GuessFormSet(prefix='guess')
            alphabet_formset = AlphabetFormSet(prefix='alphabet')
            context['form'] = form
            context['guess_formset'] = guess_formset
            context['alphabet_formset'] = alphabet_formset
            # render immediately so we don't override the form below
            user.save()
            return render(request, 'pages/games/guessle.html', context)
            
        attempt_number = 1
        form = GuessleForm(initial={})
        form.fields['attempts_left'].initial= 1
        form.fields['attempt_number'].initial = 1
        guess_formset = GuessFormSet(prefix='guess')
        alphabet_formset = AlphabetFormSet(prefix='alphabet')
        guess_form = guess_formset[attempt_number-1]

        i=1
        for guess_form in guess_formset:
            x_ref = 'guess_'+str(i)
            guess_form.fields['guess'].widget.attrs.update({'x-ref':x_ref,'x-model':x_ref+'_xmodel'})
            i=i+1

        #initiate the variables to send to the template
        context['form'] = form
        context['guess_formset'] = guess_formset
        context['alphabet_formset'] = alphabet_formset
        context['stars'] = stars

    context['t_word'] = TARGET_WORD


    #send back the html template
    user.save()
    return render(request, 'pages/games/guessle.html', context)

def supporter(request):
    return render(request=request,template_name='pages/games/guessle_support.html')

@login_required(login_url="/accounts/login/")
def guessle_hard(request):
    #get user
    user = get_object_or_404(User, pk=request.user.id)
    # print(f"User support: {user.supporter}")
    if user.supporter == False:
        return HttpResponseRedirect(reverse("game:supporterredirect"))
    else:

        #initiate array for alphabet colors
        AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
        alphabet_formset = AlphabetFormSet(form_kwargs={'empty_permitted': False}, prefix='alphabet')
        #initiate formset for guesslist
        GuessFormSet = formset_factory(GuessFormHard, extra=1, max_num=1)

        context = {}
        # Get today's todays date
        today_dt = timezone.localtime(timezone.now())
        today = today_dt  # keep variable name used elsewhere for created datetimes
        today_date = today_dt.date()

        # Check for number of daily stars
        stars = _get_daily_stars_for_date(user, today_dt)
        # Check for previous attempts
        attempts = HardGuessle_Attempt.objects.filter(date__date=today_date, user=user).order_by('-date')
        
        # add numeric count for templates/JS to use (always present)
        context['attempts_count'] = attempts.count() if attempts is not None else 0
        
        # query if a word has been created already today in the DB.
        if OneshotWordHard.objects.filter(date__date=today_date).exists():
            # get today's saved hard oneshot entry
            todaysGuessle = OneshotWordHard.objects.filter(date__date=today_date)[0] 
            todaysword = todaysGuessle
            todayclues = getattr(todaysGuessle, "clues", None)
            TARGET_WORD = getattr(todaysGuessle, "word", todaysGuessle)
            # normalise today's TARGET_WORD to a plain string
            if hasattr(TARGET_WORD, "word"):
                TARGET_WORD = TARGET_WORD.word
            elif not isinstance(TARGET_WORD, str):
                TARGET_WORD = str(TARGET_WORD)
            
            # coerce clue fields to plain strings (handle Word model instances)
            def _clue_text(c):
                if c is None:
                    return ""
                if hasattr(c, "word"):
                    return c.word
                return str(c)

            clues = [
                _clue_text(getattr(todayclues, "clue1", None)),
                _clue_text(getattr(todayclues, "clue2", None)),
                _clue_text(getattr(todayclues, "clue3", None)),
                _clue_text(getattr(todayclues, "clue4", None)),
                _clue_text(getattr(todayclues, "clue5", None)),
            ]
        else:
            # get a new word for today if one doesn't exist
            todaysword = get_random_word(difficulty = "hard")
            # get todays random clues
            clue_texts = get_random_clues(todaysword.word, difficulty="hard")
            # Debug + normalize: ensure we have a list of full-word strings
            # print("DEBUG get_random_clues returned (type):", type(clue_texts), "repr:", repr(clue_texts))
            if isinstance(clue_texts, str):
                # defensive: if a string was returned, wrap into list (string indexed -> single chars bug)
                # prefer to split on whitespace if that is a possible format, else treat as single word
                if " " in clue_texts:
                    clue_texts = clue_texts.split()
                else:
                    clue_texts = [clue_texts]
            # ensure list length >=5: if not, expand with fallback (fetch from DB)
            if not isinstance(clue_texts, (list, tuple)) or len(clue_texts) < 5:
                qs = WordsHard.objects if False else Word.objects  # regular -> Word
                fallback = []
                for cand in qs.filter():  # simplest fallback
                    w = str(getattr(cand, "word", cand)).lower()
                    if w != str(todaysword.word).lower() and len(w) == len(str(todaysword.word)):
                        fallback.append(w)
                        if len(fallback) == 5:
                            break
                # merge keeping existing items first
                clue_texts = list(clue_texts) + [c for c in fallback if c not in clue_texts]
            # final trim/pad to length 5
            clue_texts = (clue_texts + [""]*5)[:5]
            
            clues_obj, _ = OneshotCluesHard.objects.update_or_create(
                clue1 = clue_texts[0],
                clue2 = clue_texts[1],
                clue3 = clue_texts[2],
                clue4 = clue_texts[3],
                clue5 = clue_texts[4]
            )
            oneshot_obj, _ = OneshotWordHard.objects.update_or_create(
                word=todaysword.word,
                defaults={"clues": clues_obj, "date": today},
            )

            # use the created oneshot as today's guessle
            todaysGuessle = oneshot_obj
            todayclues = clues_obj
            TARGET_WORD = todaysGuessle.word
            if hasattr(TARGET_WORD, "word"):
                TARGET_WORD = TARGET_WORD.word
            elif not isinstance(TARGET_WORD, str):
                TARGET_WORD = str(TARGET_WORD)

            # build plain-string clues list
            def _clue_text(c):
                if c is None:
                    return ""
                if hasattr(c, "word"):
                    return c.word
                return str(c)

            clues = [
                _clue_text(getattr(todayclues, "clue1", None)),
                _clue_text(getattr(todayclues, "clue2", None)),
                _clue_text(getattr(todayclues, "clue3", None)),
                _clue_text(getattr(todayclues, "clue4", None)),
                _clue_text(getattr(todayclues, "clue5", None)),
            ]
            # increment frequency on the todaysword model if present
            try:
                todaysword.frequency = (todaysword.frequency or 0) + 1
                todaysword.save()
            except Exception:
                pass
        
        # This section will add each clue to the guessle rows with the correct colour for each letter.
        cluesRow,alphabet = get_clues_rows(clues, TARGET_WORD, difficulty="hard")
        
        # ensure target word is always present in context (needed by client JS)
        context['t_word'] = str(TARGET_WORD or "")
    
        new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.data,prefix='alphabet')
        context['alphabet_formset'] = new_alphabet_formset
        context['cluesRow'] = cluesRow
        context['guessleNo'] = todaysGuessle.id
        context['coloured_alpha'] = alphabet
        context['stars'] = stars
        context['difficulty'] = 'hard'
       
        # Dealing with the post of a guess
        if request.method == 'POST':   
            
            #load the 5-words scrabble dictionary
            if settings.DEBUG:
                six_letter_words = find('dicts/6-letter-words.txt')
                with open(six_letter_words, "r") as f:
                    data = f.readlines() # json.load(f)
            else:
                with open(r'oneshot_guessle/game/dicts/6-letter-words.txt') as f:
                    data =f.readlines()
            en_list = []
            for item in range(0, len(data)):
                wd = data[item].rstrip('\n')
                en_list.append(wd)
            
            #initiate array for alphabet colors
            AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
            
            #initiate formset for guesslist
            GuessFormSet = formset_factory(GuessFormHard, extra=1, max_num=1)
            #read the forms from copy of request.POST to make them mutable
            guess_formset = GuessFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='guess')
            alphabet_formset = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='alphabet')
            form = GuessleFormHard(request.POST.copy())
            
            if guess_formset.is_valid() & form.is_valid() & alphabet_formset.is_valid():
                
                # Get form data
                guess = form.cleaned_data['guess'].lower()
                attempts_left = form.cleaned_data['attempts_left']
                attempt_number = form.cleaned_data['attempt_number']
                
                #check if entered word is in dictionary
                if guess in en_list:
                    #valid attempt to increment
                    form.data['attempt_number'] = attempt_number+ 1
                    form.data['attempts_left'] = attempts_left - 1

                    #get the latest word
                    guess_form = guess_formset[attempt_number-1]
                    guess_form.cleaned_data['guess'] = guess
                    
                    # Display the result of the guess
                    row, alphabet=guess_result(guess, TARGET_WORD, alphabet)     
                    cluesRow.append(row)   
                    # new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                    context['form'] = form
                    context['alphabet_formset'] = new_alphabet_formset
                    context['cluesRow'] = cluesRow
                    
                    if guess == TARGET_WORD:
                        messages.add_message(request=request, level=messages.SUCCESS, message='You Guessled in one Shot!! ')
                        todaysGuessle.attempts+=1
                        todaysGuessle.correctAnswers+=1
                        todaysGuessle.save()
                        stars.stars += 1
                        user.stars += 1
                        stars.save()
                        context['stars'] = stars
                    elif attempts_left == 1:
                        messages.add_message(request=request, level=messages.ERROR, message = 'Chances are over. word is '+TARGET_WORD)
                        todaysGuessle.attempts+=1
                        todaysGuessle.save()
                    
                    att = HardGuessle_Attempt.objects.update_or_create(
                            user=user,
                            date=today,
                            word=todaysGuessle,
                            guess=guess
                        )
                else:
                    messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                    context['guess_formset_hard'] = guess_formset
                    context['form'] = form
                    context['alphabet_formset'] = alphabet_formset

            else:
                print(form.errors)
                print(form.non_field_errors)
                print(guess_formset.errors)
                print(guess_formset.non_form_errors())
                print(alphabet_formset.errors)
                print(alphabet_formset.non_form_errors())
        
        
        else:
            # not a POST: if the user already attempted today show their attempt and coloured result
            previous_attempt = attempts.first() if attempts.exists() else None
            if previous_attempt:
                # show message and populate the form with the previous guess (readonly behaviour)
                messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's hard Guessle")
                # pre-fill form with the user's previous guess and zero attempts left
                form = GuessleForm(initial={
                    'guess':previous_attempt.guess,
                    'attempts_left':0,
                    'attempt_number': 0,
                })
                attempt_number = 0
                # compute coloured row & alphabet from the previous guess
                row, alphabet = guess_result(previous_attempt.guess, TARGET_WORD, alphabet)
                cluesRow.append(row)
                context['cluesRow'] = cluesRow
                context['attempts'] = attempts
                # prepare small readonly formsets (keeps template expectation of formsets)
                guess_formset = GuessFormSet(prefix='guess')
                alphabet_formset = AlphabetFormSet(prefix='alphabet')
                context['form'] = form
                context['guess_formset'] = guess_formset
                context['alphabet_formset'] = alphabet_formset
                # render immediately so we don't override the form below
                user.save()
                return render(request, 'pages/games/guessle.html', context)
        
            attempt_number = 1
            form = GuessleFormHard(initial={})
            form.fields['attempts_left'].initial= 1
            form.fields['attempt_number'].initial = 1
            guess_formset = GuessFormSet(prefix='guess')
            alphabet_formset = AlphabetFormSet(prefix='alphabet')
            guess_form = guess_formset[attempt_number-1]

            i=1
            for guess_form in guess_formset:
                x_ref = 'guess_'+str(i)
                guess_form.fields['guess'].widget.attrs.update({'x-ref':x_ref,'x-model':x_ref+'_xmodel'})
                i=i+1

            #initiate the variables to send to the template
            context['form'] = form
            context['guess_formset_hard'] = guess_formset
            context['alphabet_formset'] = alphabet_formset
            context['stars'] = stars

        context['t_word'] = TARGET_WORD

        #send back the html template
        user.save()
        return render(request, 'pages/games/guessle.html', context)


def history(request):
    #dailyOsW = OneshotWord.objects.all()
    dailyOsW = OneshotWord.objects.annotate(
    last_action=Subquery(
        OneshotWord.objects.filter(
            word=OuterRef('pk')
        ).order_by('-date').values('word')[:1]
    )
)

    guessles = {}
    # Loops through all words excluding today's date or last word
    for i in range(0,len(dailyOsW)-1):
        # if percentage correct for the day is 0 stops division by 0 error
        try:
            per=round((dailyOsW[i].correctAnswers/dailyOsW[i].attempts)*100,2)
        except:
            per=0
        a = {i:{'id':dailyOsW[i].id, 'word':dailyOsW[i].word, 'clue1':dailyOsW[i].clues.clue1, 'clue2':dailyOsW[i].clues.clue2,
             'clue3':dailyOsW[i].clues.clue3,'clue4':dailyOsW[i].clues.clue4,'clue5':dailyOsW[i].clues.clue5,'per':per, 'date':dailyOsW[i].date}}
        # adds each item in the guesses and clues tables to a dict
        guessles.update(a)
    context = {'guessles':guessles}
    
    return render(request, 'pages/games/history.html', context)

def halloffame(request):
    users = User.objects.all().order_by("-stars","-highestStreak", "-streak", "-dayscorrect")
    
    table = {}
    for person in range(0,len(users)):
        rank=person+1
        username=users[person].username
        streak=users[person].streak
        highestStreak=users[person].highestStreak
        correct=users[person].dayscorrect
        incorrect=users[person].daysincorrect
        days=correct+incorrect
        stars=users[person].stars
        try:
            per=round((correct/days)*100,2)
        except:
            per=0
        a = {rank:{'username':username,'streak':streak,'highestStreak':highestStreak,
                   'correct':correct,'days':days,'per':per, 'stars':stars}}
        table.update(a)

    paginator = Paginator(tuple(table.items()), 10)
    page_number = request.GET.get('page')
    user_scores = paginator.get_page(page_number)
    context = {'user_scores':user_scores}
    
    if request.htmx:
        return render(request, "pages/games/partials/top10users.html", context)
    else:
        return render(request, 'pages/games/fame.html', context)
    

def help_menu(request):
    return render(request=request,template_name='pages/games/help.html')

def privacy_policy(request):
    return render(request=request,template_name='pages/games/policies/privacy_policy.html')

def terms_and_conditions(request):
    return render(request=request,template_name='pages/games/policies/terms_and_conditions.html')

def support_menu(request):
    return render(request=request,template_name='pages/games/support.html')

def disclaimer(request):
    return render(request=request,template_name='pages/games/policies/disclaimer.html')

def shareto_modal(request):
    return render(request=request,template_name='pages/games/shareto.html')

def results(request):
    user = get_object_or_404(User, pk=request.user.id)
    context = {}
    try:
        per=round((user.dayscorrect/(user.daysincorrect+user.dayscorrect))*100,2)
    except:
        per=0
    
    results = {'streak':user.streak,'highestStreak':user.highestStreak,'correct':user.dayscorrect,
            'incorrect':user.daysincorrect,'days':user.dayscorrect+user.daysincorrect,
            'per':per, 'stars':user.stars}
                
    context['result'] = results
    return render(request=request, template_name='pages/games/results.html',context=context)
