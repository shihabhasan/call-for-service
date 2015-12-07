from django.core.management.base import BaseCommand
from core.models import Call
import datetime as dt
import math
from django.db import connection

class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        latest_call = Call.objects.order_by('-time_received')[0]
        interval = dt.datetime.now() - latest_call.time_received
        weeks = int(interval.total_seconds() / (60 * 60 * 24 * 7))

        print("Shifting data {} weeks forward...".format(weeks))

        if weeks > 0:
            print("Shifting calls...")
            with connection.cursor() as cursor:
                cursor.execute("""
    UPDATE call SET time_received = time_received + INTERVAL %s,
                    time_routed = time_routed + INTERVAL %s,
                    time_finished = time_finished + INTERVAL %s,
                    first_unit_dispatch = first_unit_dispatch + INTERVAL %s,
                    first_unit_enroute = first_unit_enroute + INTERVAL %s,
                    first_unit_arrive = first_unit_arrive + INTERVAL %s,
                    first_unit_transport = first_unit_transport + INTERVAL %s,
                    last_unit_clear = last_unit_clear + INTERVAL %s,
                    time_closed = time_closed + INTERVAL %s;
                """, ("{} days".format(weeks * 7),) * 9)

                cursor.execute("""
    UPDATE call SET year_received = EXTRACT(ISOYEAR FROM time_received),
                    month_received = EXTRACT(MONTH FROM time_received),
                    dow_received = EXTRACT(ISODOW FROM time_received) - 1,
                    week_received = EXTRACT(WEEK FROM time_received);
                """)

