# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20160628_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='geojson_url',
            field=models.CharField(null=True, blank=True, max_length=255),
        ),
    ]
