from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.forms.formsets import formset_factory
from django.contrib import messages
from datetime import timedelta, datetime
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

User = get_user_model()

from django.core.mail import send_mail

from .forms import GuessleForm, GuessForm, GuessleFormHard, GuessFormHard, AlphabetForm
from .models import *
from .functions import guess_result, get_random_clues, get_clues_rows
# from .forms import MessageForm

ENCODING_FORMAT='utf8' 

# Create your views here.
def load_words(request):
    # opening JSON words file
    # file_ = staticfiles_storage.url('dicts/words.json') #static('dicts/words.json')
    if settings.DEBUG:
        file_ = find('dicts/words.txt')
        with open(file_) as f:
            data =f.read()
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
        print(f"Adding 5 Letter Words {round((item/lenOfData)*100,2)}%")
    
    if settings.DEBUG:
        file_ = find('dicts/6-letter-words.txt')
        with open(file_) as f:
            data =f.read()
    else:
        with open(r'oneshot_guessle/game/dicts/6-letter-words.txt') as f:
            data = f.readlines() # json.load(f)
    
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
    if difficulty == "hard":
        return WordsHard.objects.filter(Q(lastOccurance__lte=datetime.now() - timedelta(days=730)) | Q(frequency=0)).order_by('?')[0]
    else:
        return Word.objects.filter(Q(lastOccurance__lte=datetime.now() - timedelta(days=730)) | Q(frequency=0)).order_by('?')[0]


def guessle(request):   
    #initiate array for alphabet colors
    AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
    alphabet_formset = AlphabetFormSet(form_kwargs={'empty_permitted': False}, prefix='alphabet')
    #initiate formset for guesslist
    GuessFormSet = formset_factory(GuessForm, extra=1, max_num=1)

    context = {}
    # Get today's todays date
    current_dateTime =datetime.now(tz=timezone.utc)
    current_year=current_dateTime.year
    current_month=current_dateTime.month
    current_day=current_dateTime.day
    
    start_date = datetime(year=current_year, month=current_month, day=current_day, hour=0, minute=0, second=0) # represents 00:00:00
    end_date = datetime(year=current_year, month=current_month, day=current_day, hour=23, minute=59, second=59) # represents 23:59:59

    if request.user.is_authenticated:
        #get user
        user = get_object_or_404(User, pk=request.user.id)
        # Check for number of daily stars
        stars = Daily_Stars.objects.update_or_create(date__range=(start_date, end_date), user=user)
        stars = Daily_Stars.objects.filter(date__range=(start_date, end_date), user=user)[0]
        context['stars'] = stars
        # Check for previous attempts
        attempts = Guessle_Attempt.objects.filter(date__range=(start_date, end_date), user=user)
    
    # query if a word has been created already today in the DB.
    if OneshotWord.objects.filter(date__range=(start_date, end_date)).exists():
        todaysword = OneshotWord.objects.filter(date__range=(start_date, end_date))[0] 
    else:
        # get a new word for today if one doesn't exist
        todaysword = get_random_word()
        # get todays random clues
        todayclues = get_random_clues(todaysword.word, difficulty="regular")
        a = OneshotClues.objects.update_or_create(
            clue1 = todayclues[0],
            clue2 = todayclues[1],
            clue3 = todayclues[2],
            clue4 = todayclues[3],
            clue5 = todayclues[4]
        )
        todayclues = OneshotClues.objects.filter(date__range=(start_date, end_date))[0]
        clues = [todayclues.clue1,todayclues.clue2,todayclues.clue3,todayclues.clue4,todayclues.clue5]
        a = OneshotWord.objects.update_or_create(
            word = todaysword,
            clues = todayclues
            )
        b = Word.objects.get(word=todaysword)
        b.frequency += 1
        b.save()
    todaysGuessle = OneshotWord.objects.all().last()
    todayclues = todaysGuessle.clues #OneshotClues.objects.filter(date__range=(start_date, end_date))[0]
    TARGET_WORD = todaysGuessle.word

    clues = [todayclues.clue1,todayclues.clue2,todayclues.clue3,todayclues.clue4,todayclues.clue5]

    # This section will add each clue to the guessle rows with the correct colour for each letter.
    cluesRow = get_clues_rows(clues, TARGET_WORD)

    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.data,prefix='alphabet')
    context['alphabet_formset'] = new_alphabet_formset
    context['cluesRow'] = cluesRow
    context['guessleNo'] = todaysGuessle.id
    
    
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
                row=guess_result(guess, TARGET_WORD)     
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
                    yesterday_start = start_date - timedelta(1)
                    yesterday_end = end_date - timedelta(1)
                    try:
                        yesterday_attempt = Guessle_Attempt.objects.filter(date__range=(yesterday_start, yesterday_end), user=user)[0]
                        if yesterday_attempt.guess == yesterday_attempt.word:
                            user.streak +=1
                            if user.streak > user.highestStreak:
                                user.highestStreak = user.streak
                    except:
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
                            date=current_dateTime,
                            word=todaysGuessle,
                            guess=guess
                        )
                    user.save()
                else:
                    messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                    context['guess_formset'] = guess_formset
                    context['form'] = form
                    context['alphabet_formset'] = alphabet_formset

                # else:
                #     messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
                #     context['guess_formset'] = guess_formset
                #     context['form'] = form
                #     context['alphabet_formset'] = alphabet_formset

        else:
            print(form.errors)
            print(form.non_field_errors)
            print(guess_formset.errors)
            print(guess_formset.non_form_errors())
            print(alphabet_formset.errors)
            print(alphabet_formset.non_form_errors())
    
    
    else:
        try:
            # print("Not a post request")
            if (attempts.exists() == True) & (attempts[0].guess == todaysGuessle.word):
                # print(f"\n todays word {todaysGuessle.word} - The guess {attempts[0].guess} \nattempt exists and is equal to todays word")
                messages.add_message(request=request, level=messages.ERROR, message=f"You have already attempted today's Guessle")
                form = GuessleForm()
                form.fields['attempts_left'].initial= 0
                form.fields['attempt_number'].initial = 0
                attempt_number = 0
                row=guess_result(attempts[0].guess, todaysGuessle.word)
                cluesRow.append(row)
                context['cluesRow'] = cluesRow
                context['attempts'] = attempts
            elif (attempts.exists() == True) & (attempts[0].guess != todaysGuessle.word):
                # print(f"\n todays word {todaysGuessle.word} - The guess {attempts[0].guess} \nattempt exists and is not equal to todays word")
                messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's Guessle")
                form = GuessleForm()
                form.fields['attempts_left'].initial= 0
                attempt_number = 0
                row=guess_result(attempts[0].guess, todaysGuessle.word)
                cluesRow.append(row)
                context['cluesRow'] = cluesRow
                context['attempts'] = attempts
            # else:
                # print(f"We do this if there is no attempt!")
                # initiate the forms
                
                # form = GuessleForm(initial={})
                # form.fields['attempts_left'].initial= 1
        except:
            pass
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
    current_dateTime =datetime.now(tz=timezone.utc)
    current_year=current_dateTime.year
    current_month=current_dateTime.month
    current_day=current_dateTime.day
    
    start_date = datetime(year=current_year, month=current_month, day=current_day, hour=0, minute=0, second=0) # represents 00:00:00
    end_date = datetime(year=current_year, month=current_month, day=current_day, hour=23, minute=59, second=59) # represents 23:59:59

    # Check for number of daily stars
    stars = Daily_Stars.objects.update_or_create(date__range=(start_date, end_date), user=user)
    stars = Daily_Stars.objects.filter(date__range=(start_date, end_date), user=user)[0]
    # Check for previous attempts
    attempts = EasyGuessle_Attempt.objects.filter(date__range=(start_date, end_date), user=user)
    # print(f"\nAttempt is: {attempts[0].guess}\n")
    # query if a word has been created already today in the DB.
    if OneshotWordEasy.objects.filter(date__range=(start_date, end_date)).exists():
        todaysword = OneshotWordEasy.objects.filter(date__range=(start_date, end_date))[0] 
    else:
        # get a new word for today if one doesn't exist
        todaysword = get_random_word()
        # get todays random clues
        todayclues = get_random_clues(todaysword.word, difficulty="easy")
        a = OneshotCluesEasy.objects.update_or_create(
            clue1 = todayclues[0],
            clue2 = todayclues[1],
            clue3 = todayclues[2],
            clue4 = todayclues[3],
            clue5 = todayclues[4]
        )
        todayclues = OneshotCluesEasy.objects.filter(date__range=(start_date, end_date))[0]
        clues = [todayclues.clue1,todayclues.clue2,todayclues.clue3,todayclues.clue4,todayclues.clue5]
        a = OneshotWordEasy.objects.update_or_create(
            word = todaysword,
            clues = todayclues
            )
        b = Word.objects.get(word=todaysword)
        b.frequency += 1
        b.save()
    todaysGuessle = OneshotWordEasy.objects.all().last()
    todayclues = todaysGuessle.clues #OneshotClues.objects.filter(date__range=(start_date, end_date))[0]
    TARGET_WORD = todaysGuessle.word

    clues = [todayclues.clue1,todayclues.clue2,todayclues.clue3,todayclues.clue4,todayclues.clue5]

    # This section will add each clue to the guessle rows with the correct colour for each letter.
    cluesRow = get_clues_rows(clues, TARGET_WORD, difficulty="easy")
    
    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.data,prefix='alphabet')
    context['alphabet_formset'] = new_alphabet_formset
    context['cluesRow'] = cluesRow
    context['guessleNo'] = todaysGuessle.id
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
                row=guess_result(guess, TARGET_WORD)     
                cluesRow.append(row)   
                # new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                context['form'] = form
                # context['guess_formset'] = new_guess_formset
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
                        date=current_dateTime,
                        word=todaysGuessle,
                        guess=guess
                    )
            else:
                messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                context['guess_formset'] = guess_formset
                context['form'] = form
                context['alphabet_formset'] = alphabet_formset

            # else:
            #     messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
            #     context['guess_formset'] = guess_formset
            #     context['form'] = form
            #     context['alphabet_formset'] = alphabet_formset

        else:
            print(form.errors)
            print(form.non_field_errors)
            print(guess_formset.errors)
            print(guess_formset.non_form_errors())
            print(alphabet_formset.errors)
            print(alphabet_formset.non_form_errors())
    
    
    else:
        try:
            # print("Not a post request")
            if (attempts.exists() == True) & (attempts[0].guess == todaysGuessle.word):
                # print(f"\n todays word {todaysGuessle.word} - The guess {attempts[0].guess} \nattempt exists and is equal to todays word")
                messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's easy Guessle")
                form = GuessleForm()
                form.fields['attempts_left'].initial= 0
                form.fields['attempt_number'].initial = 0
                attempt_number = 0
                row=guess_result(attempts[0].guess, todaysGuessle.word)
                cluesRow.append(row)
                context['cluesRow'] = cluesRow
                context['attempts'] = attempts
            elif (attempts.exists() == True) & (attempts[0].guess != todaysGuessle.word):
                # print(f"\n todays word {todaysGuessle.word} - The guess {attempts[0].guess} \nattempt exists and is not equal to todays word")
                messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's easy Guessle")
                form = GuessleForm()
                form.fields['attempts_left'].initial= 0
                attempt_number = 0
                row=guess_result(attempts[0].guess, todaysGuessle.word)
                cluesRow.append(row)
                context['cluesRow'] = cluesRow
                context['attempts'] = attempts
            # else:
                # print(f"We do this if there is no attempt!")
                # initiate the forms
                
                # form = GuessleForm(initial={})
                # form.fields['attempts_left'].initial= 1
        except:
            pass
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

    #send back the html template
    user.save()
    return render(request, 'pages/games/guessle.html', context)

def supporter(request):
    return render(request=request,template_name='pages/games/guessle_support.html')

@login_required(login_url="/accounts/login/")
def guessle_hard(request):
    #get user
    user = get_object_or_404(User, pk=request.user.id)
    print(f"User support: {user.supporter}")
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
        current_dateTime =datetime.now(tz=timezone.utc)
        current_year=current_dateTime.year
        current_month=current_dateTime.month
        current_day=current_dateTime.day
        
        start_date = datetime(year=current_year, month=current_month, day=current_day, hour=0, minute=0, second=0) # represents 00:00:00
        end_date = datetime(year=current_year, month=current_month, day=current_day, hour=23, minute=59, second=59) # represents 23:59:59

        # Check for number of daily stars
        stars = Daily_Stars.objects.update_or_create(date__range=(start_date, end_date), user=user)
        stars = Daily_Stars.objects.filter(date__range=(start_date, end_date), user=user)[0]
        # Check for previous attempts
        attempts = HardGuessle_Attempt.objects.filter(date__range=(start_date, end_date), user=user)
        # print(f"\nAttempt is: {attempts[0].guess}\n")
        # query if a word has been created already today in the DB.
        if OneshotWordHard.objects.filter(date__range=(start_date, end_date)).exists():
            todaysword = OneshotWordHard.objects.filter(date__range=(start_date, end_date))[0] 
        else:
            # get a new word for today if one doesn't exist
            todaysword = get_random_word(difficulty = "hard")
            # get todays random clues
            todayclues = get_random_clues(todaysword.word, difficulty="hard")
            a = OneshotCluesHard.objects.update_or_create(
                clue1 = todayclues[0],
                clue2 = todayclues[1],
                clue3 = todayclues[2],
                clue4 = todayclues[3],
                clue5 = todayclues[4]
            )
            todayclues = OneshotCluesHard.objects.filter(date__range=(start_date, end_date))[0]
            clues = [todayclues.clue1,todayclues.clue2,todayclues.clue3,todayclues.clue4,todayclues.clue5]
            a = OneshotWordHard.objects.update_or_create(
                word = todaysword,
                clues = todayclues
                )
            b = WordsHard.objects.get(word=todaysword)
            b.frequency += 1
            b.save()
        todaysGuessle = OneshotWordHard.objects.all().last()
        todayclues = todaysGuessle.clues #OneshotClues.objects.filter(date__range=(start_date, end_date))[0]
        TARGET_WORD = todaysGuessle.word
        print(f"Todays word is : {TARGET_WORD}")
        clues = [todayclues.clue1,todayclues.clue2,todayclues.clue3,todayclues.clue4,todayclues.clue5]

        # This section will add each clue to the guessle rows with the correct colour for each letter.
        cluesRow = get_clues_rows(clues, TARGET_WORD, difficulty="hard")
        
        new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.data,prefix='alphabet')
        context['alphabet_formset'] = new_alphabet_formset
        context['cluesRow'] = cluesRow
        context['guessleNo'] = todaysGuessle.id
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
            print(f"guess formset : {guess_formset}")
            alphabet_formset = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='alphabet')
            form = GuessleFormHard(request.POST.copy())
            print("Before checkinf if forms are valid")
            if guess_formset.is_valid() & form.is_valid() & alphabet_formset.is_valid():
                print("forms are valid")    
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
                    row=guess_result(guess, TARGET_WORD)     
                    cluesRow.append(row)   
                    # new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                    context['form'] = form
                    # context['guess_formset'] = new_guess_formset
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
                            date=current_dateTime,
                            word=todaysGuessle,
                            guess=guess
                        )
                else:
                    messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                    context['guess_formset_hard'] = guess_formset
                    context['form'] = form
                    context['alphabet_formset'] = alphabet_formset

                # else:
                #     messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
                #     context['guess_formset'] = guess_formset
                #     context['form'] = form
                #     context['alphabet_formset'] = alphabet_formset

            else:
                print(form.errors)
                print(form.non_field_errors)
                print(guess_formset.errors)
                print(guess_formset.non_form_errors())
                print(alphabet_formset.errors)
                print(alphabet_formset.non_form_errors())
        
        
        else:
            try:
                # print("Not a post request")
                if (attempts.exists() == True) & (attempts[0].guess == todaysGuessle.word):
                    # print(f"\n todays word {todaysGuessle.word} - The guess {attempts[0].guess} \nattempt exists and is equal to todays word")
                    messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's hard Guessle")
                    form = GuessleFormHard()
                    form.fields['attempts_left'].initial= 0
                    form.fields['attempt_number'].initial = 0
                    attempt_number = 0
                    row=guess_result(attempts[0].guess, todaysGuessle.word)
                    cluesRow.append(row)
                    context['cluesRow'] = cluesRow
                    context['attempts'] = attempts
                elif (attempts.exists() == True) & (attempts[0].guess != todaysGuessle.word):
                    # print(f"\n todays word {todaysGuessle.word} - The guess {attempts[0].guess} \nattempt exists and is not equal to todays word")
                    messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's hard Guessle")
                    form = GuessleFormHard()
                    form.fields['attempts_left'].initial= 0
                    attempt_number = 0
                    row=guess_result(attempts[0].guess, todaysGuessle.word)
                    cluesRow.append(row)
                    context['cluesRow'] = cluesRow
                    context['attempts'] = attempts
                # else:
                    # print(f"We do this if there is no attempt!")
                    # initiate the forms
                    
                    # form = GuessleForm(initial={})
                    # form.fields['attempts_left'].initial= 1
            except:
                pass
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

        #send back the html template
        user.save()
        return render(request, 'pages/games/guessle.html', context)


def history(request):
    dailyOsW = OneshotWord.objects.all()
    # clues = OneshotClues.objects.all()

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
    context = {'players':table}
    
    return render(request, 'pages/games/fame.html', context)

def help_menu(request):
    return render(request=request,template_name='pages/games/help.html')

def support_menu(request):
    return render(request=request,template_name='pages/games/support.html')

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
