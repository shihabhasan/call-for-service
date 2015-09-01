from django.test import TestCase
from .models import Call


class CallTestCase(TestCase):
    def setUp(self):
        Call.objects.create(call_id=1)

    def test_calls_can_be_queried(self):
        calls = Call.objects.all()
        self.assertEqual(calls.count(), 1)

