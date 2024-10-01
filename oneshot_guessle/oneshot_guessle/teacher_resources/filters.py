from django import template

register = template.Library()

@register.filter
def has_purchased(user, resource):
    return user.purchase_set.filter(resource_id=resource.id).exists()