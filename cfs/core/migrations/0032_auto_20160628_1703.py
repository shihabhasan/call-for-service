# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20160628_1701'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteconfiguration',
            name='geo_se_bound',
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='geo_sw_bound',
            field=geoposition.fields.GeopositionField(max_length=42, blank=True, verbose_name='Southwest bound'),
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='geo_center',
            field=geoposition.fields.GeopositionField(max_length=42, blank=True, verbose_name='Center'),
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='geo_default_zoom',
            field=models.PositiveIntegerField(verbose_name='Default zoom level', default=11),
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='geo_ne_bound',
            field=geoposition.fields.GeopositionField(max_length=42, blank=True, verbose_name='Northeast bound'),
        ),
    ]
