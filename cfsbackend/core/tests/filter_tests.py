from ..filters import CallFilter
from ..models import Call, District, CallUnit, Squad

from django.test import TestCase
from datetime import timedelta


class CallFilterTest(TestCase):
    def setUp(self):
        d1 = District.objects.create(district_id=1, descr="D1")
        d2 = District.objects.create(district_id=2, descr="D2")
        sq1 = Squad.objects.create(squad_id=1)
        sq2 = Squad.objects.create(squad_id=2)
        cu1 = CallUnit.objects.create(call_unit_id=1, squad_id=1)
        cu2 = CallUnit.objects.create(call_unit_id=2, squad_id=1)
        cu3 = CallUnit.objects.create(call_unit_id=3, squad_id=2)
        self.c1 = Call.objects.create(call_id=1, time_received='2015-01-01T09:00-05:00', district=d1, primary_unit=cu1,
                                 officer_response_time=timedelta(seconds=1))
        self.c2 = Call.objects.create(call_id=2, time_received='2015-01-02T09:00-05:00', district=d2, primary_unit=cu2,
                                 first_dispatched=cu1, officer_response_time=timedelta(seconds=90))
        self.c3 = Call.objects.create(call_id=3, time_received='2015-01-03T09:00-05:00', district=d2, primary_unit=cu3,
                                 first_dispatched=cu2, reporting_unit=cu1,
                                 officer_response_time=timedelta(minutes=5, seconds=1))

    def test_duration_filter(self):
        filter = CallFilter({"officer_response_time_0": "00:00:02"}, queryset=Call.objects.all())
        assert self.c1 not in filter.qs
        assert self.c2 in filter.qs
        assert self.c3 in filter.qs

        filter = CallFilter({"officer_response_time_1": "00:01:30"}, queryset=Call.objects.all())
        assert self.c1 in filter.qs
        assert self.c2 in filter.qs
        assert self.c3 not in filter.qs

        filter = CallFilter({"officer_response_time_0": "00:00:02", "officer_response_time_1": "00:01:30"}, queryset=Call.objects.all())
        assert self.c1 not in filter.qs
        assert self.c2 in filter.qs
        assert self.c3 not in filter.qs


    def test_unit_filter(self):
        filter = CallFilter({"primary_unit": 1})
        assert filter.qs.count() == 1

        filter = CallFilter({"unit": 1})
        assert filter.qs.count() == 3

        filter = CallFilter({"unit": 2})
        assert filter.qs.count() == 2

        filter = CallFilter({"unit": 3})
        assert filter.qs.count() == 1

    def test_squad_filter(self):
        filter = CallFilter({"squad": 1})
        assert filter.qs.count() == 3

        filter = CallFilter({"squad": 2})
        assert filter.qs.count() == 1
