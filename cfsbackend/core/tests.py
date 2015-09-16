from rest_framework.test import APITestCase
from .models import Call, Incident
from datetime import datetime
from rest_framework.test import APIRequestFactory


class CallTestCase(APITestCase):

    def setUp(self):
        Call.objects.create(call_id=1, time_received='2015-01-01')
        Call.objects.create(call_id=2, time_received='2015-01-02')
        Call.objects.create(call_id=3, time_received='2015-01-03')

    def test_calls_can_be_queried(self):
        calls = Call.objects.all()
        self.assertEqual(calls.count(), 3)

    def test_time_received_can_be_queried(self):
        response = self.client.get('/api/calls/?time_received_0=2015-01-02')
        self.assertEqual(response.data['count'], 2)

class IncidentTestCase(APITestCase):

     def setUp(self):
         Incident.objects.create(incident_id=1, time_filed='2015-01-01')

     def test_incidents_can_be_queried(self):
        incidents = Incident.objects.all()

        self.assertEqual(incidents.count(), 1)

     def test_time_filed_can_be_queried(self):
        response = self.client.get('/api/incidents/?time_filed_0=2015-01-01')
        self.assertEqual(response.data['count'], 1)
