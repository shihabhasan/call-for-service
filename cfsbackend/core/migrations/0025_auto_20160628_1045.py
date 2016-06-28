# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_call_zip_code_str'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='cancelled',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='report_only',
            field=models.BooleanField(default=False),
        ),
    ]
