# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0016_auto_20160621_1553'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'verbose_name_plural': 'cities'},
        ),
        migrations.AlterModelOptions(
            name='priority',
            options={'verbose_name_plural': 'priorities'},
        ),
    ]
