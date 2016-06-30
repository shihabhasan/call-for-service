# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20160627_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calllog',
            name='call',
        ),
        migrations.AddField(
            model_name='calllog',
            name='call_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
