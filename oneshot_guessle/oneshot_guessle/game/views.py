from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
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

import plotly.graph_objects as go

User = get_user_model()

from django.core.mail import send_mail

from .forms import GuessleForm, GuessForm, AlphabetForm
from .models import Word, OneshotWord, OneshotClues, Guessle_Attempt
from .functions import guess_result
# from .forms import MessageForm

ENCODING_FORMAT='utf8' 

# Create your views here.
def load_words(request):
    # opening JSON words file
    # file_ = staticfiles_storage.url('dicts/words.json') #static('dicts/words.json')
    if settings.DEBUG:
        file_ = find('dicts/words.txt')
    else:
        file_ = static('dicts/words.txt')
    with open(file_, "r") as f:
        data = f.readlines() # json.load(f)

    newWords = 0
    lenOfData = len(data)
    for item in range(0, len(data)):
        wd = data[item].rstrip('\n')  
        if not Word.objects.filter(word=wd).exists():
            obj = Word.objects.update_or_create(
                word = wd
            )
            newWords += 1
        print(f"{round((item/lenOfData)*100,2)}%")
    msg = f"Added {newWords} new words."
    context = {'msg':msg}
    return render(request, 'pages/games/words_loaded.html', context)# HttpResponse(msg, content_type='text/plain')

def get_random_word():
    return Word.objects.filter(Q(lastOccurance__lte=datetime.now() - timedelta(days=730)) | Q(frequency=0)).order_by('?')[0]

def get_random_clues(oneshotWord):
    cows,bulls = [], []
    newclue=5
    # checks to make sure that there are no more than 1 correct placed guesses
    # and no more than 2 incorrect placed guesses
    cows_list = len(cows)
    bulls_list = len(bulls)
    while not(bulls_list == 1 and cows_list ==3):
        cows,bulls = [], []
        clues = Word.objects.order_by('?')
        
        clue1,clue2,clue3,clue4,clue5 = clues[0],clues[1],clues[2],clues[3],clues[4]
        
        # This makes sure that none of the clues are the same as the daily word
        while clue1==oneshotWord:
            clue1=clues[newclue]
            newclue+=1
        while clue2==oneshotWord:
            clue2=clues[newclue]
            newclue+=1
        while clue3==oneshotWord:
            clue3=clues[newclue]
            newclue+=1
        while clue4==oneshotWord:
            clue4=clues[newclue]
            newclue+=1
        while clue5==oneshotWord:
            clue5=clues[newclue]
            newclue+=1
        clues_list = [clue1,clue2,clue3,clue4,clue5]
        
        print(f"oneshotword: {oneshotWord} -- Clues: {clues_list}")
        # checking for cows (letters that are in the word but not in the correct place
        for word in clues_list:
            for letter in word.word:
                if letter in oneshotWord:
                    if letter not in cows:
                        cows.append(letter)
        
        # checking for bulls (letters in a word that are in the correct place)
        for word in clues_list:
            
            for char in range(0,len(oneshotWord)):
                # checks if each character in the clues are in the same place as the daily word
                if word.word[char]==oneshotWord[char]:
                    # makes sure the letter is not already in the list of bulls
                    # before adding the word to the list
                    if word.word[char] not in bulls:
                        bulls.append(word.word[char])
                        # Checks if the bull is already in the cows. It should be!
                        if word.word[char] in cows:
                            # find the index position of the cow and remove it.
                            placement = cows.index(word.word[char])
                            cows.pop(placement)
                            
        cows_list = len(cows)
        bulls_list = len(bulls)                        
        
        # print(f"Cows: {cows_list} -- Bulls: {bulls_list}")
    return clues_list

@login_required(login_url="/accounts/login/")
def guessle(request):
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

    # Check for previous attempts
    attempts = Guessle_Attempt.objects.filter(date__range=(start_date, end_date), user=user)
    # print(f"\nAttempt is: {attempts[0].guess}\n")
    # query if a word has been created already today in the DB.
    if OneshotWord.objects.filter(date__range=(start_date, end_date)).exists():
        todaysword = OneshotWord.objects.filter(date__range=(start_date, end_date))[0] 
    else:
        # get a new word for today if one doesn't exist
        todaysword = get_random_word()
        # get todays random clues
        todayclues = get_random_clues(todaysword.word)
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
    cluesRow = []
    for clue in range(0,5):
        cows,bulls=[],[]
        row='<div class="btn-group">'
        guess = clues[clue]                
        for j in range(0,5):
            letter_color = 'l'+str(j+1)+'_color'
            if guess[j] == TARGET_WORD[j]:
                letter= '<button style="height:60px;width:60px;" class="form-control btn btn-success fw-bold text-center text-light fs-5 disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet_formset[ord(guess[j])-97].data['l_color'] = 'btn-success'
                bulls.append(guess[j])
                row+=letter
            elif guess[j] in TARGET_WORD and guess[j] not in cows and guess[j] not in bulls:
                letter= '<button style="height:60px;width:60px;" class="form-control btn btn-warning fw-bold text-center text-light fs-5 disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet_formset[ord(guess[j])-97].data['l_color'] = 'btn-warning'
                row+=letter
                cows.append(guess[j])
            else:
                letter= '<button style="height:60px;width:60px;" class="form-control btn btn-secondary fw-bold text-center text-light fs-5 disabled" type="text", size="1">'+guess[j].upper()+'</button>'
                alphabet_formset[ord(guess[j])-97].data['l_color'] = 'btn-secondary'
                row+=letter
        row+='</div><br>'
        cluesRow.append(row)

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
            five_letter_words = static('dicts/5-letter-words.json')
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
                
                # Display hte result of the guess
                row=guess_result(guess, TARGET_WORD)     
                cluesRow.append(row)   
                # new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                context['form'] = form
                # context['guess_formset'] = new_guess_formset
                context['alphabet_formset'] = new_alphabet_formset
                context['cluesRow'] = cluesRow

                if guess == TARGET_WORD:
                    messages.add_message(request=request, level=messages.SUCCESS, message='You Guessled in one Shot!! Challenge your friend by clicking '+'<a href='+request.path+'?target_word='+form.cleaned_data['target_word']+'>here</a>', extra_tags='safe')
                    results = request.session.get('results',None)
                    todaysGuessle.attempts+=1
                    todaysGuessle.correctAnswers+=1
                    todaysGuessle.save()
                    print(f"Days correct {user.dayscorrect}")
                    user.dayscorrect+=1
                    yesterday = datetime.now() - timedelta(1)
                    userrun = Guessle_Attempt.objects.filter(date=yesterday)
                    if userrun.exists():
                        user.streak +=1
                        if user.streak > user.highestStreak:
                            user.highestStreak = user.streak
                    else:
                        user.streak = 0
                    if results:
                        results[str(attempt_number)] = results[str(attempt_number)]+1
                    else:
                        results = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0}
                        results[str(attempt_number)] = 1

                    request.session['results'] = results
                    
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
                messages.add_message(request=request, level=messages.ERROR, message="You have already attempted today's Guessle")
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

        #see if the word is in the link, else get a new word encrypt and store in form
        # if request.GET.get('target_word',None) == None:
        #     target_word = todaysword
        #     encrypted_word = target_word
        #     form.fields['target_word'].initial = encrypted_word
            
        # else:
        #     request.GET._mutable = True
        #     encrypted_word = request.GET.get('target_word')
        #     form.fields['target_word'].initial = encrypted_word
        #     request.GET['target_word'] = None

        #initiate the variables to send to the template
        context['form'] = form
        context['guess_formset'] = guess_formset
        context['alphabet_formset'] = alphabet_formset

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
    users = User.objects.all().order_by("-highestStreak", "-streak", "-dayscorrect")
    table = {}
    for person in range(0,len(users)):
        rank=person+1
        username=users[person].username
        streak=users[person].streak
        highestStreak=users[person].highestStreak
        correct=users[person].dayscorrect
        incorrect=users[person].daysincorrect
        days=correct+incorrect
        try:
            per=round((correct/days)*100,2)
        except:
            per=0
        a = {rank:{'username':username,'streak':streak,'highestStreak':highestStreak,
                   'correct':correct,'days':days,'per':per}}
        table.update(a)
    context = {'players':table}
    
    return render(request, 'pages/games/fame.html', context)

def help_menu(request):
    return render(request=request,template_name='pages/games/help.html')

def results(request):
    user = get_object_or_404(User, pk=request.user.id)
    context = {}
    
    
    results = {'streak':user.streak,'highestStreak':user.highestStreak,'correct':user.dayscorrect,
            'incorrect':user.daysincorrect,'days':user.dayscorrect+user.daysincorrect,
            'per':round((user.dayscorrect/user.daysincorrect)*100,2)}
                
    context['result'] = results
    return render(request=request, template_name='pages/games/results.html',context=context)
