# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160628_1525'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='siteconfiguration',
            options={'verbose_name': '* Site Configuration'},
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_beat',
            field=models.BooleanField(default=False, verbose_name='Use beat?'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_district',
            field=models.BooleanField(default=False, verbose_name='Use district?'),
        ),
    ]
