from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.shortcuts import render, redirect
import json
from datetime import date, timedelta, datetime
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
                word = wd,
            )
            newWords += 1
        print(f"{round((item/lenOfData)*100,2)}%")
    msg = f"Added {newWords} new words."
    context = {'msg':msg}
    return render(request, 'pages/games/words_loaded.html', context)# HttpResponse(msg, content_type='text/plain')

def get_random_word():
    startdate = date.today()
    enddate = startdate + timedelta(days=730)
    return Word.objects.filter(sampledate__gte=date(enddate)).order_by('?')[0]


def wordle(request):
    # https://codepen.io/nht007/pen/jOaPNRg?editors=1000
    # https://codepen.io/ThatAladdin/pen/NWwaVjb?editors=0010
    # https://codepen.io/nht007/pen/jOaPNRg?editors=0010 
    # https://github.com/ragsub/wordle DAJNGO!!!!!!
    # Todays Date
    today=date.today()
    print(today)
    
    # Check no words have been selected for today
    if not OneshotWord.objects.filter(date=today):
        # get a new word for today
        todaysword = get_random_word()
        a = OneshotWord.create(word = todaysword)
        a.save()
        b = Word.objects.get(word=todaysword)
        b.frequency += 1
        b.save()
    else:
        todaysword = OneshotWord.objects.filter(date=today)
    
    context = {'todaysword':todaysword}
    return render(request, 'pages/games/wordle.html', context)