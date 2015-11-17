from datetime import timedelta
from dateutil.parser import parse as dtparse

from django import forms
from django.http import QueryDict
from django.test import TestCase

from ..filters import create_filterset, create_rel_filterset, OfficerActivityFilterSet
from ..models import Call, District, CallUnit, Squad, CallSource, ZipCode, \
        OfficerActivity, Nature


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
        self.n1 = Nature.objects.create(nature_id=1, descr='Robbery')
        self.n2 = Nature.objects.create(nature_id=2, descr='Homicide')
        self.call1 = Call.objects.create(call_id=1, time_received='2014-01-15T9:00', nature=self.n1)
        self.call2 = Call.objects.create(call_id=2, time_received='2014-03-18T3:00', nature=self.n2)
        self.cu1 = CallUnit.objects.create(call_unit_id=1, descr='A1')
        self.cu2 = CallUnit.objects.create(call_unit_id=2, descr='B2')

        self.a1 = OfficerActivity.objects.create(officer_activity_id=1,
                activity="IN CALL",
                time=dtparse('2014-01-15T9:00'),
                call_unit=self.cu1,
                call=self.call1)
        self.a2 = OfficerActivity.objects.create(officer_activity_id=2,
                activity="IN CALL",
                time=dtparse('2014-01-15T9:10'),
                call_unit=self.cu2,
                call=self.call1)
        self.a3 = OfficerActivity.objects.create(officer_activity_id=3,
                activity="IN CALL",
                time=dtparse('2014-01-15T10:00'),
                call_unit=self.cu1,
                call=self.call2)
        self.a4 = OfficerActivity.objects.create(officer_activity_id=4,
                activity="IN CALL",
                time=dtparse('2014-01-16T9:50'),
                call_unit=self.cu2,
                call=self.call2)
        self.a5 = OfficerActivity.objects.create(officer_activity_id=5,
                activity="OUT OF SERVICE",
                time=dtparse('2014-01-16T10:10'),
                call_unit=self.cu1,
                call=None)
        self.a6 = OfficerActivity.objects.create(officer_activity_id=6,
                activity="OUT OF SERVICE",
                time=dtparse('2014-01-18T9:00'),
                call_unit=self.cu2,
                call=None)


    def test_call_unit_filter(self):
        filter_set = OfficerActivityFilterSet(data=QueryDict("call_unit=1"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a1, qs)
        self.assertIn(self.a3, qs)
        self.assertIn(self.a5, qs)
        self.assertEqual(3, len(qs))

        filter_set = OfficerActivityFilterSet(data=QueryDict("call_unit!=1"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a2, qs)
        self.assertIn(self.a4, qs)
        self.assertIn(self.a6, qs)
        self.assertEqual(3, len(qs))

    def test_call_filter(self):
        # Here we use nature as a proxy for call_id, since we can't filter on
        # that; we just need to uniquely identify the call for this test case.
        filter_set = OfficerActivityFilterSet(data=QueryDict("call__nature=1"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a1, qs)
        self.assertIn(self.a2, qs)
        self.assertEqual(2, len(qs))

        filter_set = OfficerActivityFilterSet(data=QueryDict("call__nature!=1"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a3, qs)
        self.assertIn(self.a4, qs)
        self.assertIn(self.a5, qs)
        self.assertIn(self.a6, qs)
        self.assertEqual(4, len(qs))

    def test_time_filter(self):
        filter_set = OfficerActivityFilterSet(data=QueryDict("time__gte=2014-01-16"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a4, qs)
        self.assertIn(self.a5, qs)
        self.assertIn(self.a6, qs)
        self.assertEqual(3, len(qs))

        filter_set = OfficerActivityFilterSet(data=QueryDict("time__lte=2014-01-15"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a1, qs)
        self.assertIn(self.a2, qs)
        self.assertIn(self.a3, qs)
        self.assertEqual(3, len(qs))

    def test_activity_filter(self):
        filter_set = OfficerActivityFilterSet(data=QueryDict("activity__exact=IN+CALL"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a1, qs)
        self.assertIn(self.a2, qs)
        self.assertIn(self.a3, qs)
        self.assertIn(self.a4, qs)
        self.assertEqual(4, len(qs))

        filter_set = OfficerActivityFilterSet(data=QueryDict("activity__exact!=IN+CALL"),
                queryset=OfficerActivity.objects.all())
        qs = filter_set.filter()
        self.assertIn(self.a5, qs)
        self.assertIn(self.a6, qs)
        self.assertEqual(2, len(qs))



class CallFilterSetTest(TestCase):
    def setUp(self):
        cs1 = CallSource.objects.create(call_source_id=1,
                                        descr="Self Initiated")
        cs2 = CallSource.objects.create(call_source_id=2, descr="911 Call")
        d1 = District.objects.create(district_id=1, descr="D1")
        d2 = District.objects.create(district_id=2, descr="D2")
        sq1 = Squad.objects.create(squad_id=1)
        sq2 = Squad.objects.create(squad_id=2)
        cu1 = CallUnit.objects.create(call_unit_id=1, squad_id=1)
        cu2 = CallUnit.objects.create(call_unit_id=2, squad_id=1)
        cu3 = CallUnit.objects.create(call_unit_id=3, squad_id=2)
        self.c1 = Call.objects.create(call_id=1,
                                      time_received='2015-01-01T09:00-05:00',
                                      district=d1, primary_unit=cu1,
                                      officer_response_time=timedelta(
                                          seconds=1), call_source=cs1)
        self.c2 = Call.objects.create(call_id=2,
                                      time_received='2015-01-02T09:00-05:00',
                                      district=d2, primary_unit=cu2,
                                      first_dispatched=cu1,
                                      officer_response_time=timedelta(
                                          seconds=90), call_source=cs1)
        self.c3 = Call.objects.create(call_id=3,
                                      time_received='2015-01-03T09:00-05:00',
                                      district=d2, primary_unit=cu3,
                                      first_dispatched=cu2, reporting_unit=cu1,
                                      officer_response_time=timedelta(minutes=5,
                                                                      seconds=1),
                                      call_source=cs2)

        # def test_duration_filter(self):
        #     filter = CallFilter({"officer_response_time_0": "00:00:02"}, queryset=Call.objects.all())
        #     assert self.c1 not in filter.qs
        #     assert self.c2 in filter.qs
        #     assert self.c3 in filter.qs
        #
        #     filter = CallFilter({"officer_response_time_1": "00:01:30"}, queryset=Call.objects.all())
        #     assert self.c1 in filter.qs
        #     assert self.c2 in filter.qs
        #     assert self.c3 not in filter.qs
        #
        #     filter = CallFilter({"officer_response_time_0": "00:00:02", "officer_response_time_1": "00:01:30"}, queryset=Call.objects.all())
        #     assert self.c1 not in filter.qs
        #     assert self.c2 in filter.qs
        #     assert self.c3 not in filter.qs
        #
        #
        # def test_unit_filter(self):
        #     filter = CallFilter({"primary_unit": 1})
        #     assert filter.qs.count() == 1
        #
        #     filter = CallFilter({"unit": 1})
        #     assert filter.qs.count() == 3
        #
        #     filter = CallFilter({"unit": 2})
        #     assert filter.qs.count() == 2
        #
        #     filter = CallFilter({"unit": 3})
        #     assert filter.qs.count() == 1
        #
        # def test_squad_filter(self):
        #     filter = CallFilter({"squad": 1})
        #     assert filter.qs.count() == 3
        #
        #     filter = CallFilter({"squad": 2})
        #     assert filter.qs.count() == 1
        #
        # def test_initiated_by_filter(self):
        #     filter = CallFilter({"initiated_by": "Citizen"})
        #     assert filter.qs.count() == 1
        #
        #     filter = CallFilter({"initiated_by": "Self"})
        #     assert filter.qs.count() == 2
