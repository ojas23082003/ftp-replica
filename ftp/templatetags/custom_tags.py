from django import template

register = template.Library()

@register.filter(name="check")
def check(value):
    if value == "yes" or value == "Male":
        return True
    elif value == "no" or value == "Female":
        return False