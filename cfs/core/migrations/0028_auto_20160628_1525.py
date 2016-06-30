# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20160628_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_call_source',
            field=models.BooleanField(verbose_name='Use call sources?', default=False),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_nature',
            field=models.BooleanField(verbose_name='Use natures?', default=False),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='use_nature_group',
            field=models.BooleanField(verbose_name='Use nature groups?', default=False),
        ),
    ]
