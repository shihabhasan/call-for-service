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

                print("Shifting call log data...")
                cursor.execute("""
    UPDATE call_log SET time_recorded = time_recorded + INTERVAL %s;
                """, ("{} days".format(weeks*7),))
                
                print("Shifting call notes...")
                cursor.execute("""
    UPDATE note SET time_recorded = time_recorded + INTERVAL %s;
                """, ("{} days".format(weeks*7),))

                print("Shifting officer allocation data...")
                cursor.execute("""
    UPDATE shift_unit SET in_time = in_time + INTERVAL %s,
                          out_time = out_time + INTERVAL %s;
                """, ("{} days".format(weeks*7),) * 2)

                cursor.execute("""
    UPDATE out_of_service SET start_time = start_time + INTERVAL %s,
                          end_time = end_time + INTERVAL %s;
                """, ("{} days".format(weeks*7),) * 2)

                print("Recreating materialized views...")
                # Drop old view dependent on hardcoded time sample
                cursor.execute("""
    DROP MATERIALIZED VIEW discrete_officer_activity;
                """)

                # Figure out the new time range for the time sample view
                cursor.execute("SELECT MIN(time_) FROM time_sample;")
                prev_start = cursor.fetchone()[0]

                new_start = prev_start + dt.timedelta(days=weeks*7)
                new_end = new_start + dt.timedelta(days=365)

                # Recreate the time sample view
                cursor.execute("""
    DROP MATERIALIZED VIEW time_sample;
    CREATE MATERIALIZED VIEW time_sample AS
        SELECT series.time_
            FROM generate_series(
                %s::timestamp without time zone,
                %s::timestamp without time zone,
                '00:10:00'::interval
            ) series(time_);
                """, (new_start.strftime("%Y-%m-%d %H:%M:%S"),
                      new_end.strftime("%Y-%m-%d %H:%M:%S")))

                # Reindex the time sample view
                cursor.execute("""
    CREATE UNIQUE INDEX time_sample_time_ndx
        ON time_sample(time_);
                """)

                # Refresh other views
                cursor.execute("""
    REFRESH MATERIALIZED VIEW in_call;
    REFRESH MATERIALIZED VIEW officer_activity;
                """)

                # Recreate the DOA view
                cursor.execute("""
    CREATE MATERIALIZED VIEW discrete_officer_activity AS
      SELECT
        ROW_NUMBER() OVER (ORDER BY start_time ASC) AS discrete_officer_activity_id,
        ts.time_,
        oa.call_unit_id,
        oa.officer_activity_type_id,
        oa.call_id
      FROM
        officer_activity oa,
        time_sample ts
      WHERE
        ts.time_ BETWEEN oa.start_time AND oa.end_time;
                """)

                # Reindex the DOA view
                cursor.execute("""
    CREATE INDEX discrete_officer_activity_time
      ON discrete_officer_activity(time_);
      
    CREATE INDEX discrete_officer_activity_time_hour
      ON discrete_officer_activity (EXTRACT(HOUR FROM time_));
                """)
