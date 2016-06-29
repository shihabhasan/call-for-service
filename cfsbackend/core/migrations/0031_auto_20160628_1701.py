# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20160628_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='geo_center',
            field=geoposition.fields.GeopositionField(max_length=42, blank=True),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='geo_default_zoom',
            field=models.PositiveIntegerField(default=11),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='geo_ne_bound',
            field=geoposition.fields.GeopositionField(max_length=42, blank=True),
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='geo_se_bound',
            field=geoposition.fields.GeopositionField(max_length=42, blank=True),
        ),
    ]
