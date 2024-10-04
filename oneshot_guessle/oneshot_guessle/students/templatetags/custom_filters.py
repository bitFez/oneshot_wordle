from django import template

register = template.Library()

@register.filter
def percentage_format(value, decimal_places=0):
    try:
        # Convert the input value to a float and multiply by 100
        percent_value = float(value) * 100
        # Format the percentage value as a string with the specified number of decimal places
        return f"{percent_value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return ""  # Return an empty string if conversion fails