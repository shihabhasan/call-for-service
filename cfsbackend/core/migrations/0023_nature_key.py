# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160627_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='nature',
            name='key',
            field=models.CharField(max_length=10, unique=True, blank=True, null=True),
        ),
    ]
