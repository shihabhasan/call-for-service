# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_change_call_id_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='street_address',
            field=models.CharField(null=True, blank=True, max_length=255),
        ),
        migrations.RunSQL(
            """
            UPDATE call SET street_address =
            CAST(street_num AS CHAR) || ' ' || street_name;
            """
        ),
        migrations.RemoveField(
            model_name='call',
            name='street_name',
        ),
        migrations.RemoveField(
            model_name='call',
            name='street_num',
        ),
    ]
