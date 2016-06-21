import json

from django import template
from django.utils.html import mark_safe
from django.forms.models import model_to_dict as _model_to_dict

register = template.Library()


@register.filter
def jsonify(value):
    return mark_safe(json.dumps(value))


@register.filter
def model_to_dict(value):
    return _model_to_dict(value)
