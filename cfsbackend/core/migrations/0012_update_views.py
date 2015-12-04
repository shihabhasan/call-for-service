# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
import os.path

base_dir = os.path.realpath(os.path.dirname(__file__))


def sql_path(filename):
    return os.path.join(base_dir, "sql", filename)

with open(sql_path("0012_call_general_category.sql")) as file:
    call_general_category_sql = file.read()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_add_indexes'),
    ]

    operations = [
        migrations.RunSQL(call_general_category_sql),
    ]
