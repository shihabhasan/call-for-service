# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0019_auto_20160627_1348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calllog',
            old_name='call_id',
            new_name='_call_id'
        ),
        migrations.AddField(
            model_name='calllog',
            name='call_id',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.RunSQL("""
            UPDATE call_log SET call_id = cast(_call_id as VARCHAR(64));
        """),
        migrations.RemoveField(
            model_name='calllog',
            name='_call_id'
        ),
    ]
