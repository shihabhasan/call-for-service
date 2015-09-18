from rest_framework.test import APITestCase

from ..models import Call, District


class CallTestCase(APITestCase):
    
    def setUp(self):
        d1 = District.objects.create(district_id=1, descr="D1")
        d2 = District.objects.create(district_id=2, descr="D2")
        Call.objects.create(call_id=1, time_received='2015-01-01T09:00-05:00', district=d1)
        Call.objects.create(call_id=2, time_received='2015-01-02T09:00-05:00', district=d2)
        Call.objects.create(call_id=3, time_received='2015-01-03T09:00-05:00', district=d2)

    def test_calls_can_be_queried(self):
        response = self.client.get('/api/calls/')
        self.assertEqual(response.data['count'], 3)

    def test_time_received_can_be_queried(self):
        response = self.client.get('/api/calls/?time_received_0=2015-01-02')
        self.assertEqual(response.data['count'], 2)
        
    def test_district_can_be_queried(self):
        response = self.client.get('/api/calls/?district=1')
        self.assertEqual(response.data['count'], 1)