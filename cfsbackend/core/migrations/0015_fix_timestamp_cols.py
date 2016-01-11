# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import migrations, models

base_dir = os.path.realpath(os.path.dirname(__file__))

def sql_path(filename):
    return os.path.join(base_dir, "sql", filename)

with open(sql_path("in_call.sql")) as file:
    in_call_sql = file.read()
with open(sql_path("officer_activity.sql")) as file:
    officer_activity_sql = file.read()
with open(sql_path("discrete_officer_activity.sql")) as file:
    discrete_officer_activity_sql = file.read()



timestamp_cols = [
    ('note', 'time_recorded'),
    ('shift_unit', 'in_time'),
    ('shift_unit', 'out_time'),
]

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20151208_1039'),
    ]

    operations = [
        # Have to drop this to alter column types
        migrations.RunSQL("DROP MATERIALIZED VIEW discrete_officer_activity"),
        migrations.RunSQL("DROP MATERIALIZED VIEW officer_activity"),
        migrations.RunSQL("DROP MATERIALIZED VIEW in_call"),
        migrations.RunSQL(
            ["ALTER TABLE {} ALTER {} TYPE timestamp without time zone".format(table, col) for table, col in timestamp_cols]
        ),
        migrations.RunSQL(in_call_sql),
        migrations.RunSQL(officer_activity_sql),
        migrations.RunSQL(discrete_officer_activity_sql),
    ]
