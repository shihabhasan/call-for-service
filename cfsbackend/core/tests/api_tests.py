from rest_framework.test import APITestCase

from ..models import Call, District, CallUnit, Squad


class CallTestCase(APITestCase):
    
    def setUp(self):
        d1 = District.objects.create(district_id=1, descr="D1")
        d2 = District.objects.create(district_id=2, descr="D2")
        sq1 = Squad.objects.create(squad_id=1, descr="A")
        sq2 = Squad.objects.create(squad_id=2, descr="B")
        cu1 = CallUnit.objects.create(call_unit_id=1, descr="U1", squad=sq1)
        cu2 = CallUnit.objects.create(call_unit_id=2, descr="U2", squad=sq1)
        cu3 = CallUnit.objects.create(call_unit_id=3, descr="U3", squad=sq2)
        Call.objects.create(call_id=1, time_received='2015-01-01T09:00-05:00', district=d1,
                primary_unit=cu1, reporting_unit=cu2, first_dispatched=cu3)
        Call.objects.create(call_id=2, time_received='2015-01-02T09:00-05:00', district=d2,
                primary_unit=cu2, reporting_unit=cu3, first_dispatched=cu1)
        Call.objects.create(call_id=3, time_received='2015-01-03T09:00-05:00', district=d2,
                primary_unit=cu3, reporting_unit=cu1, first_dispatched=cu2)

    def test_calls_can_be_queried(self):
        response = self.client.get('/api/calls/')
        self.assertEqual(response.data['count'], 3)

    def test_time_received_can_be_queried(self):
        response = self.client.get('/api/calls/?time_received_0=2015-01-02')
        self.assertEqual(response.data['count'], 2)
        
    def test_district_can_be_queried(self):
        response = self.client.get('/api/calls/?district=1')
        self.assertEqual(response.data['count'], 1)

    def test_call_unit_can_be_queried(self):
        response = self.client.get('/api/calls/?primary_unit=1')
        self.assertEqual(response.data['count'],1)

        response = self.client.get('/api/calls/?reporting_unit=3')
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/api/calls/?first_dispatched=2')
        self.assertEqual(response.data['count'],1)

        response = self.client.get('/api/calls/?unit=1')
        self.assertEqual(response.data['count'], 3)

    def test_squad_can_be_queried(self):
        response = self.client.get('/api/calls/?primary_unit__squad=1')
        self.assertEqual(response.data['count'],2)

        response = self.client.get('/api/calls/?reporting_unit__squad=1')
        self.assertEqual(response.data['count'], 2)

        response = self.client.get('/api/calls/?first_dispatched__squad=2')
        self.assertEqual(response.data['count'],1)

        response = self.client.get('/api/calls/?squad=1')
        self.assertEqual(response.data['count'], 3)
