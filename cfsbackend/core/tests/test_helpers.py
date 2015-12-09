from django.http import QueryDict
from dateutil.parser import parse as dtparse
from datetime import timedelta

from core.models import Call, Transaction, CallLog, \
        InCallPeriod, OutOfServicePeriod, ShiftUnit, \
        Shift, OfficerActivity


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

def create_officer_activity(**kwargs):
    """
    Build the underlying data required to show the
    described OfficerActivity instance; since OfficerActivity
    is a view, we can't create objects in it directly.

    We have to refresh the views afterward, since they're
    materialized.

    This will not work properly if the data is not realistic;
    for example, you need to have an ON DUTY activity for an
    officer for that officer to get picked up in other
    activity types.
    """
    activity_type = kwargs.get('activity_type')
    time = kwargs.get('time')
    call_unit = kwargs.get('call_unit')
    call = kwargs.get('call')

    if activity_type is None or time is None:
        raise ValueError('activity_type and time must be given to create OfficerActivity.')

    if activity_type.descr.startswith('IN CALL'):
        dispatch, _ = Transaction.objects.get_or_create(descr='Dispatched',
                code='D')
        cleared, _ = Transaction.objects.get_or_create(descr='Cleared',
                code='C')
        CallLog.objects.create(transaction=dispatch,
                time_recorded=(time-timedelta(minutes=1)),
                call=call,
                call_unit=call_unit)
        CallLog.objects.create(transaction=cleared,
                time_recorded=(time+timedelta(minutes=1)),
                call=call,
                call_unit=call_unit)

        InCallPeriod.update_view()
    
    elif activity_type.descr == 'OUT OF SERVICE':
        OutOfServicePeriod.objects.create(call_unit=call_unit,
                start_time=(time-timedelta(minutes=1)),
                end_time=(time+timedelta(minutes=1)))

    elif activity_type.descr == 'ON DUTY':

        su = ShiftUnit.objects.create(call_unit=call_unit,
                in_time=(time-timedelta(minutes=1)),
                out_time=(time+timedelta(minutes=1)))

        # Need to associate a shift with this shift_unit --
        # just give it the shift unit's shift_unit_id, so
        # we know it's unique
        s = Shift.objects.create(shift_id=su.shift_unit_id)
        su.shift = s
        su.save()

    else:
        raise ValueError('Unrecognized activity_type: %s' % activity_type.descr)

    OfficerActivity.update_view()

    # Return the objects created with the given kwargs, so we can compare the instance we think
    # we've created to what we've actually created
    return OfficerActivity.objects.filter(**kwargs)

