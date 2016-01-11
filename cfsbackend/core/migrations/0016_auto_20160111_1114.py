# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models
import os

base_dir = os.path.realpath(os.path.dirname(__file__))

def sql_path(filename):
    return os.path.join(base_dir, "sql", filename)

with open(sql_path("in_call.sql")) as file:
    in_call_sql = file.read()
with open(sql_path("officer_activity.sql")) as file:
    officer_activity_sql = file.read()
with open(sql_path("discrete_officer_activity.sql")) as file:
    discrete_officer_activity_sql = file.read()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_fix_timestamp_cols'),
    ]

    operations = [
        migrations.RunSQL("DROP MATERIALIZED VIEW discrete_officer_activity"),
        migrations.RunSQL("DROP MATERIALIZED VIEW officer_activity"),
        migrations.RunSQL("DROP MATERIALIZED VIEW in_call"),

        migrations.AlterField(
            model_name='call',
            name='first_unit_arrive',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_dispatch',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_enroute',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_transport',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='last_unit_clear',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_closed',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_finished',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_received',
            field=core.models.DateTimeNoTZField(db_index=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_routed',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calllog',
            name='time_recorded',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='time_recorded',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='outofserviceperiod',
            name='end_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='outofserviceperiod',
            name='start_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shiftunit',
            name='in_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shiftunit',
            name='out_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),

        migrations.RunSQL(in_call_sql),
        migrations.RunSQL(officer_activity_sql),
        migrations.RunSQL(discrete_officer_activity_sql),

    ]
