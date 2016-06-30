# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
import os, os.path

base_dir = os.path.realpath(os.path.dirname(__file__))


timestamp_cols = [
    ('call', 'time_received'),
    ('call', 'time_routed'),
    ('call', 'time_finished'),
    ('call', 'first_unit_dispatch'),
    ('call', 'first_unit_enroute'),
    ('call', 'first_unit_arrive'),
    ('call', 'first_unit_transport'),
    ('call', 'last_unit_clear'),
    ('call', 'time_closed'),
    ('call_log', 'time_recorded'),
    ('out_of_service', 'start_time'),
    ('out_of_service', 'end_time'),
]


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_auto_20151201_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='officer_response_time',
            field=models.DurationField(db_index=True, blank=True, null=True),
        ),
        migrations.AlterIndexTogether(
            name='call',
            index_together=set([('dow_received', 'hour_received')]),
        ),
        migrations.RunSQL([
            ("CREATE INDEX call_day_trunc_time_received_ndx ON call (DATE_TRUNC('day', time_received))", None),
            ("CREATE INDEX call_hour_trunc_time_received_ndx ON call (DATE_TRUNC('hour', time_received))", None)
        ])
    ]
