# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20160628_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_cancelled',
            field=models.BooleanField(default=False, verbose_name='Use cancelled?'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_priority',
            field=models.BooleanField(default=False, verbose_name='Use priority?'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_shift',
            field=models.BooleanField(default=False, verbose_name='Use shift?'),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_squad',
            field=models.BooleanField(default=False, verbose_name='Use squad?'),
        ),
    ]
