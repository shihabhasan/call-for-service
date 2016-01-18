from datetime import timedelta
from dateutil.parser import parse as dtparse
from django import forms
from django.http import QueryDict
from django.test import TestCase
from ..filters import create_filterset, create_rel_filterset, \
    OfficerActivityFilterSet, CallFilterSet
from ..models import Call, District, CallUnit, Squad, CallSource, ZipCode, \
    OfficerActivity, Nature, OfficerActivityType, Beat, CallLog, InCallPeriod, \
    OutOfServicePeriod, Transaction, ShiftUnit, Shift
from .test_helpers import create_call, create_officer_activity


def test_create_simple_filterset():
    TestDistrictFilterSet = create_filterset(
        District,
        [
            {"name": "district_id"},
            {"name": "descr", "label": "Description",
             "lookups": ["icontains", "iexact"]}
        ],
        name="TestDistrictFilterSet"
    )

    filter_set = TestDistrictFilterSet()
    filter_names = sorted(filter_set.get_filters().keys())
    assert filter_names == ["descr", "district_id"]


def test_create_rel_filterset():
    ZipCodeFilterSet = create_rel_filterset("ZipCode")
    assert ZipCodeFilterSet.Meta.model == ZipCode


def test_create_complex_filterset():
    CallFilterSet = create_filterset(
        Call,
        [
            {"name": "district", "rel": "District"},
            {"name": "zip_code", "label": "ZIP Code", "rel": "ZipCode"},
            {"name": "time_received", "type": "date",
             "lookups": ["gte", "lte"]},
            {"name": "officer_response_time", "type": "duration",
             "lookups": ["gte", "lte"]},
            {"name": "cancelled", "type": "boolean"},
        ]
    )

    filter_set = CallFilterSet()
    filters = filter_set.get_filters()
    filter_names = sorted(filters.keys())

    assert filter_names == ["cancelled", "district", "officer_response_time",
                            "time_received", "zip_code"]
    assert filters["zip_code"].__class__.__name__ == "ZipCodeFilterSet"
    assert filters["district"].__class__.__name__ == "DistrictFilterSet"

    time_received = filters["time_received"]
    assert type(time_received.form_field) == forms.DateField

    cancelled = filters["cancelled"]
    assert type(cancelled.form_field) == forms.BooleanField


class OfficerActivityFilterSetTest(TestCase):
    def setUp(self):
        cs1 = CallSource.objects.create(call_source_id=1,
                descr='Citizen Initiated', code='C')
        cs2 = CallSource.objects.create(call_source_id=2,
                descr='Self Initiated', code='S')
        self.n1 = Nature.objects.create(nature_id=1, descr='Robbery')
        self.n2 = Nature.objects.create(nature_id=2, descr='Homicide')
        self.call1 = create_call(call_id=1,
                                 time_received='2014-01-15T9:00',
                                 nature=self.n1,
                                 call_source=cs1)
        self.call2 = create_call(call_id=2,
                                 time_received='2014-03-18T3:00',
                                 nature=self.n2,
                                 call_source=cs1)

        self.b1 = Beat.objects.create(beat_id=1, descr='B1')
        self.b2 = Beat.objects.create(beat_id=2, descr='B2')

        self.d1 = District.objects.create(district_id=1, descr='D1')
        self.d2 = District.objects.create(district_id=2, descr='D2')

        self.cu1 = CallUnit.objects.create(call_unit_id=1, descr='A1',
                                           beat=self.b1, district=self.d1)
        self.cu2 = CallUnit.objects.create(call_unit_id=2, descr='B2',
                                           beat=self.b2, district=self.d2)

        self.at1 = OfficerActivityType.objects.create(
            officer_activity_type_id=1,
            descr="IN CALL - CITIZEN INITIATED")
        self.at2 = OfficerActivityType.objects.create(
            officer_activity_type_id=2,
            descr="OUT OF SERVICE")
        self.at3 = OfficerActivityType.objects.create(
            officer_activity_type_id=3,
            descr="ON DUTY")


        self.a1 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-15T9:00'),
                                                 call_unit=self.cu1,
                                                 call=self.call1)
        self.a2 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-15T9:10'),
                                                 call_unit=self.cu2,
                                                 call=self.call1)
        self.a3 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-15T10:00'),
                                                 call_unit=self.cu1,
                                                 call=self.call2)
        self.a4 = create_officer_activity(activity_type=self.at1,
                                                 time=dtparse(
                                                     '2014-01-16T9:50'),
                                                 call_unit=self.cu2,
                                                 call=self.call2)
        self.a5 = create_officer_activity(activity_type=self.at2,
                                                 time=dtparse(
                                                     '2014-01-16T10:10'),
                                                 call_unit=self.cu1,
                                                 call=None)
        self.a6 = create_officer_activity(activity_type=self.at2,
                                                 time=dtparse(
                                                     '2014-01-18T9:00'),
                                                 call_unit=self.cu2,
                                                 call=None)

        # In order for this to be realistic, for every busy activity,
        # we need to have an on duty activity
        self.a7 = create_officer_activity(activity_type=self.at3,
                                            time=dtparse('2014-01-15T9:00'),
                                            call_unit=self.cu1,
                                            call=None)
        self.a8 = create_officer_activity(activity_type=self.at3,
                                            time=dtparse('2014-01-15T9:10'),
                                            call_unit=self.cu2,
                                            call=None)
        self.a9 = create_officer_activity(activity_type=self.at3,
                                            time=dtparse('2014-01-15T10:00'),
                                            call_unit=self.cu1,
                                            call=None)
        self.a10 = create_officer_activity(activity_type=self.at3,
                                             time=dtparse('2014-01-16T9:50'),
                                             call_unit=self.cu2,
                                             call=None)
        self.a11 = create_officer_activity(activity_type=self.at3,
                                             time=dtparse('2014-01-16T10:10'),
                                             call_unit=self.cu1,
                                             call=None)
        self.a12 = create_officer_activity(activity_type=self.at3,
                                             time=dtparse('2014-01-18T9:00'),
                                             call_unit=self.cu2,
                                             call=None)


    def test_call_unit_filter(self):
        self._test_query("call_unit=1", [self.a1, self.a3, self.a5, self.a7, self.a9, self.a11])

        self._test_query("call_unit!=1", [self.a2, self.a4, self.a6, self.a8, self.a10, self.a12])

    def test_time_filter(self):
        self._test_query("time__gte=2014-01-16", [self.a4, self.a5, self.a6, self.a10, self.a11, self.a12])

        self._test_query("time__lte=2014-01-15", [self.a1, self.a2, self.a3, self.a7, self.a8, self.a9])

    def test_call_unit_beat_filter(self):
        self._test_query("call_unit__beat=1", [self.a1, self.a3, self.a5, self.a7, self.a9, self.a11])

        self._test_query("call_unit__beat!=1", [self.a2, self.a4, self.a6, self.a8, self.a10, self.a12])

    def test_call_unit_district_filter(self):
        self._test_query("call_unit__district=1", [self.a1, self.a3, self.a5, self.a7, self.a9, self.a11])

        self._test_query("call_unit__district!=1", [self.a2, self.a4, self.a6, self.a8, self.a10, self.a12])

    def _test_query(self, query, correct_results):
        filter_set = OfficerActivityFilterSet(data=QueryDict(query),
                                              queryset=OfficerActivity.objects.all())
        qs_values = filter_set.filter().values()

        for obj in correct_results:
            # Get the values of the queryset, so we can compare to given dicts
            self.assertIn(obj.values()[0], qs_values)
        self.assertEqual(len(correct_results), filter_set.filter().count())


class CallFilterSetTest(TestCase):
    def setUp(self):
        cs1 = CallSource.objects.create(call_source_id=1, code="SI",
                                        descr="Self Initiated")
        cs2 = CallSource.objects.create(call_source_id=2, code="911", descr="911 Call")
        d1 = District.objects.create(district_id=1, descr="D1")
        d2 = District.objects.create(district_id=2, descr="D2")
        sq1 = Squad.objects.create(squad_id=1, descr="S1")
        sq2 = Squad.objects.create(squad_id=2, descr="S2")
        cu1 = CallUnit.objects.create(call_unit_id=1, squad_id=1, descr="CU1")
        cu2 = CallUnit.objects.create(call_unit_id=2, squad_id=1, descr="CU2")
        cu3 = CallUnit.objects.create(call_unit_id=3, squad_id=2, descr="CU3")
        self.c1 = create_call(call_id=1,
                                      time_received='2015-01-01T09:00-05:00',
                                      district=d1, primary_unit=cu1,
                                      officer_response_time=timedelta(
                                          seconds=1), call_source=cs1)
        self.c2 = create_call(call_id=2,
                                      time_received='2015-01-02T09:00-05:00',
                                      district=d2, primary_unit=cu2,
                                      first_dispatched=cu1,
                                      officer_response_time=timedelta(
                                          seconds=90), call_source=cs1)
        self.c3 = create_call(call_id=3,
                                      time_received='2015-01-03T09:00-05:00',
                                      district=d2, primary_unit=cu3,
                                      first_dispatched=cu2, reporting_unit=cu1,
                                      officer_response_time=timedelta(minutes=5,
                                                                      seconds=1),
                                      call_source=cs2)


    def test_no_filter(self):
        filter = CallFilterSet(data=QueryDict(""), queryset=Call.objects.all())
        assert filter.filter().count() == 3

    def test_squad_filter(self):
        filter = CallFilterSet(data=QueryDict("squad=1"), queryset=Call.objects.all())
        assert filter.filter().count() == 3

        filter = CallFilterSet(data=QueryDict("squad=2"), queryset=Call.objects.all())
        assert filter.filter().count() == 1

    def test_initiated_by_filter(self):
        filter = CallFilterSet(data=QueryDict("initiated_by=1"), queryset=Call.objects.all())
        assert filter.filter().count() == 1

        filter = CallFilterSet(data=QueryDict("initiated_by=0"), queryset=Call.objects.all())
        assert filter.filter().count() == 2
