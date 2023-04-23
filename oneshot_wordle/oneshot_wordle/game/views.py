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
import json
from datetime import timedelta, datetime, date
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage


User = get_user_model()

from django.core.mail import send_mail

from .models import Word, OneshotWord
# from .forms import MessageForm

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
    clues = Word.objects.order_by('?')
    cows,bulls=0,0
    clue1,clue2,clue3,clue4,clue5 = clues[0],clues[1],clues[2],clues[3],clues[4]
    while clue1==oneshotWord:
        clue1=Word.objects.order_by('?')
    while clue2==oneshotWord:
        clue2=Word.objects.order_by('?')
    while clue3==oneshotWord:
        clue3=Word.objects.order_by('?')
    while clue4==oneshotWord:
        clue4=Word.objects.order_by('?')
    while clue5==oneshotWord:
        clue5=Word.objects.order_by('?')
    
    for letter in clue1:
        for char in oneshotWord:
            if letter==char:
                bull+=1
    return 

def wordle(request):
    # https://codepen.io/nht007/pen/jOaPNRg?editors=1000
    # https://codepen.io/ThatAladdin/pen/NWwaVjb?editors=0010
    # https://codepen.io/nht007/pen/jOaPNRg?editors=0010 
    # https://github.com/ragsub/wordle DAJNGO!!!!!!
    
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
    
    
    context = {'todaysword':todaysword}
    return render(request, 'pages/games/wordle.html', context)