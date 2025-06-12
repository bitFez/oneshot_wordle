from django import template
from ..models import DailyTangle

register = template.Library()

@register.filter(name='scrabble_value')
def scrabble_value(letter):
    return DailyTangle.get_scrabble_value(letter)

@register.filter
def get_key(dictionary, key):
    return dictionary.get(key, "")

@register.filter
def index(sequence, position):
    try:
        return sequence[position]
    except:
        return ''