from django.template.loader import render_to_string
from django.utils.html import mark_safe, format_html

def navbar(context, *args, **kwargs):
    return mark_safe("<li><a href='/officer_allocation'>Officer Allocation</a></li>")