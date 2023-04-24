from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.shortcuts import render, redirect
import json, os
from cryptography.fernet import Fernet
from django.forms.formsets import formset_factory
from django.contrib import messages
from datetime import timedelta, datetime, date
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage


User = get_user_model()

from django.core.mail import send_mail

from .forms import WordleForm, GuessForm, AlphabetForm
from .models import Word, OneshotWord, OneshotClues
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
    cows,bulls,newclue=5,5,5
    while bulls>1 or cows >3:
        cows,bulls=0,0
        clues = Word.objects.order_by('?')
        
        clue1,clue2,clue3,clue4,clue5 = clues[0],clues[1],clues[2],clues[3],clues[4]
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
        clues_list = [clue1.word,clue2.word,clue3.word,clue4.word,clue5.word]
        
        print(f"oneshotword: {oneshotWord}")
        print(f"Clues: {clues_list}")
        # checking for cows (letters that are in the word but not in the correct place
        for words in clues_list:
            for letter in words:
                if letter in oneshotWord.word:
                    cows +=1

        # checking for bulls (letters in a word that are in the correct place)
        for words in clues_list:
            for letter in words:
                for char in oneshotWord.word:
                    if letter==char:
                        bulls+=1
                        cows -=1
        

    return clues_list

def wordle(request): 
    # Get today's todays date
    today=datetime.today()
    start_date = datetime(year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0) # represents 00:00:00
    end_date = datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59) # represents 23:59:59
    
    # query if a word has been created already today in the DB.
    if OneshotWord.objects.filter(date__range=(start_date, end_date)).exists():
        todaysword = OneshotWord.objects.filter(date__range=(start_date, end_date))[0] 
    else:
        # get a new word for today if one doesn't exist
        todaysword = get_random_word()
        a = OneshotWord.objects.update_or_create(word = todaysword)
        b = Word.objects.get(word=todaysword)
        b.frequency += 1
        b.save()
    
    # get the clues for the day
    if OneshotClues.objects.filter(date__range=(start_date, end_date)).exists():
        todayclues = OneshotClues.objects.filter(date__range=(start_date, end_date))[0] 
    else:
        # get a new word for today if one doesn't exist
        todayclues = get_random_clues(todaysword)
        a = OneshotClues.objects.update_or_create(
            clue1 = todayclues[0],
            clue2 = todayclues[1],
            clue3 = todayclues[2],
            clue4 = todayclues[3],
            clue5 = todayclues[4]
        )
    
    #load the 5-words scrabble dictionary
    if settings.DEBUG:
        five_letter_words = find('dicts/5-letter-words.json')
    else:
        five_letter_words = static('dicts/5-letter-words.json')
    en_dict = json.load(open(five_letter_words))
    en_list = [en['word'] for en in en_dict]

    #initiate cryptography
    
    key = Fernet.generate_key() #this is your "password"
    cipher_suite = Fernet(key)

    #initiate array for alphabet colors
    AlphabetFormSet = formset_factory(AlphabetForm, extra=26, max_num=26)
    
    #initiate formset for guesslist
    GuessFormSet = formset_factory(GuessForm, extra=6, max_num=6)

    context = {'todaysword':todaysword, 'todayclues':todayclues}
    
    if request.method == 'POST':
        #read the forms from copy of request.POST to make them mutable
        guess_formset = GuessFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='guess')
        alphabet_formset = AlphabetFormSet(request.POST.copy(), form_kwargs={'empty_permitted': False}, prefix='alphabet')
        form = WordleForm(request.POST.copy())

        if guess_formset.is_valid() & form.is_valid() & alphabet_formset.is_valid():
            #get the target word and decrypt
            TARGET_WORD = f.decrypt(bytes(form.cleaned_data['target_word'],ENCODING_FORMAT)).decode()
            #get the other form data
            guess = form.cleaned_data['guess'].lower()
            attempts_left = form.cleaned_data['attempts_left']
            attempt_number = form.cleaned_data['attempt_number']
            
            #clear the word for the next refresh
            form.data['word'] = ""

            #check sufficient attempts are left
            if attempts_left > 0:
                #check if entered word is in dictionary
                if guess in en_list:
                    #valid attempt to increment
                    form.data['attempt_number'] = attempt_number+ 1
                    form.data['attempts_left'] = attempts_left - 1

                    #get the latest word
                    guess_form = guess_formset[attempt_number-1]
                    guess_form.cleaned_data['guess'] = guess
                    #go through each word
                    for j in range(0,5):
                        letter_color = 'l'+str(j+1)+'_color'
                        if guess[j] == TARGET_WORD[j]:
                            guess_form.cleaned_data[letter_color] = 'bg-success'
                            alphabet_formset[ord(guess[j])-97].cleaned_data['l_color'] = 'btn-success'
                        elif guess[j] in TARGET_WORD:
                            guess_form.cleaned_data[letter_color] = 'bg-warning'
                            if alphabet_formset[ord(guess[j])-97].cleaned_data['l_color'] != 'btn-success':
                                alphabet_formset[ord(guess[j])-97].cleaned_data['l_color'] = 'btn-warning'
                        else:
                            guess_form.cleaned_data[letter_color] = 'bg-secondary'
                            alphabet_formset[ord(guess[j])-97].cleaned_data['l_color'] = 'btn-secondary'
                    
                    new_guess_formset = GuessFormSet(initial = guess_formset.cleaned_data, prefix='guess')
                    new_alphabet_formset = AlphabetFormSet(initial = alphabet_formset.cleaned_data,prefix='alphabet')

                    context['form'] = form
                    context['guess_formset'] = new_guess_formset
                    context['alphabet_formset'] = new_alphabet_formset

                    if guess == TARGET_WORD:
                        messages.add_message(request=request, level=messages.SUCCESS, message='You solved it in '+ str(attempt_number) + ' attempts! Challenge your friend by clicking '+'<a href='+request.path+'?target_word='+form.cleaned_data['target_word']+'>here</a>', extra_tags='safe')
                        results = request.session.get('results',None)
                        if results:
                            results[str(attempt_number)] = results[str(attempt_number)]+1
                        else:
                            results = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0}
                            results[str(attempt_number)] = 1

                        request.session['results'] = results
                        print(results)
                    if attempts_left == 1:
                        messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
                else:
                    messages.add_message(request=request, level=messages.ERROR, message=guess+' is not a valid english word')
                    context['guess_formset'] = guess_formset
                    context['form'] = form
                    context['alphabet_formset'] = alphabet_formset

            else:
                messages.add_message(request=request, level=messages.ERROR, message = 'Chances over. word is '+TARGET_WORD)
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
        #initiate the forms
        form = WordleForm()
        form.fields['attempts_left'].initial= 6
        form.fields['attempt_number'].initial = 1
        guess_formset = GuessFormSet(prefix='guess')
        alphabet_formset = AlphabetFormSet(prefix='alphabet')
        i=1
        for guess_form in guess_formset:
                x_ref = 'guess_'+str(i)
                guess_form.fields['guess'].widget.attrs.update({'x-ref':x_ref,'x-model':x_ref+'_xmodel'})
                i=i+1

        #see if the word is in the link, else get a new word encrypt and store in form
        if request.GET.get('target_word',None) == None:
            target_word = todaysword
            encrypted_word = cipher_suite.encrypt(b"{target_word}")
            form.fields['target_word'].initial = cipher_suite.decrypt(encrypted_word)
            
        else:
            request.GET._mutable = True
            encrypted_word = request.GET.get('target_word')
            form.fields['target_word'].initial = encrypted_word
            request.GET['target_word'] = None

        #initiate the variables to send to the template
        context['form'] = form
        context['guess_formset'] = guess_formset
        context['alphabet_formset'] = alphabet_formset

    #send back the html template
    
    return render(request, 'pages/games/wordle.html', context)

def help_menu(request):
    return render(request=request,template_name='word/help.html')

def results(request):
    context = {}
    results = request.session.get('results',None)
    if results:
        df = pd.DataFrame.from_dict(results, orient='index')
    else:
        results = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0}
        df = pd.DataFrame.from_dict([results], orient='index')

    df.reset_index(inplace=True)
    df.columns = ['attempts','count']

    fig = px.bar(df, x="count", y="attempts", width=350, height=500, labels={'count':'Count','attempts':'Attempts'})
    fig.update_layout(autosize=True, margin_autoexpand=False, template='simple_white')

    context['result'] = fig.to_html(config= {'displaylogo': False, 'displayModeBar':False}, include_plotlyjs=False)
    return render(request=request, template_name='word/results.html',context=context)
