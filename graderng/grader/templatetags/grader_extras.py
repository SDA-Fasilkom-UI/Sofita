import html
from django import template

register = template.Library()


@register.filter
def index(value, arg):
    return value[arg]


@register.filter
def to_range(value):
    return range(value)


@register.filter
def div(value, arg):
    return value // arg


@register.filter
def subtract(value, arg):
    return value - arg
