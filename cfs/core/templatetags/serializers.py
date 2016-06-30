import json

from django import template
from django.utils.html import mark_safe
from django.forms.models import model_to_dict as _model_to_dict
from geoposition import Geoposition


class JSONEncoderWithGeolocation(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Geoposition):
            return [float(o.latitude), float(o.longitude)]

        return super().default(o)


register = template.Library()


@register.filter
def jsonify(value):
    return mark_safe(json.dumps(value, cls=JSONEncoderWithGeolocation))


@register.filter
def model_to_dict(value):
    return _model_to_dict(value)
