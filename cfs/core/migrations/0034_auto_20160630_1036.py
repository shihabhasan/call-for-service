# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_siteconfiguration_geojson_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='closecode',
            name='code',
            field=models.CharField(verbose_name='Unique code', max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='closecode',
            name='descr',
            field=models.CharField(verbose_name='Description', max_length=255),
        ),
    ]
