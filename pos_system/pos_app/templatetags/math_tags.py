# In your app's templatetags/math_tags.py file
from django import template
register = template.Library()

@register.simple_tag
def multiply(qty, unit_price):
    return qty * unit_price   