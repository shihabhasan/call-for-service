from django.http import QueryDict
from dateutil.parser import parse as dtparse

from core.models import Call


def assert_list_equiv(this, that):
    """
    Lists are having difficulty with equivalence, so let's try this.
    """
    assert len(this) == len(that)
    for i in range(len(this)):
        assert this[i] == that[i]

def create_call(**kwargs):
    try:
        kwargs['time_received'] = dtparse(kwargs['time_received'])
    except KeyError:
        raise ValueError("You must include a time_received value.")

    kwargs.setdefault('report_only', False)
    kwargs.setdefault('cancelled', False)

    call = Call(**kwargs)
    call.update_derived_fields()
    call.save()

    return call


def q(string):
    return QueryDict(string)
