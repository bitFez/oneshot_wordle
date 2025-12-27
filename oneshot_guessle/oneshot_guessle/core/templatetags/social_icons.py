from django import template

register = template.Library()

ICON_MAP = {
    "x": "twitter-x",
    "twitter": "twitter",
    # add other overrides here
}

@register.filter
def social_icon(name):
    if not name:
        return ""
    key = name.lower()
    return ICON_MAP.get(key, key)
