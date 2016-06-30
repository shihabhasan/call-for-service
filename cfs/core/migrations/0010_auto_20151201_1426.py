# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_create_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callsource',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='closecode',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
