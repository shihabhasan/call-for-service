# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0020_prepare_to_change_call_id_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='call_id',
            field=models.CharField(primary_key=True, max_length=64,
                                   serialize=False),
        ),
        migrations.RunSQL(
            """
            ALTER TABLE call_log ADD CONSTRAINT call_id_fk
            FOREIGN KEY (call_id) REFERENCES call (call_id)
            """,
            state_operations=[
                migrations.RemoveField(
                    model_name='calllog',
                    name='call_id',
                ),
                migrations.AddField(
                    model_name='calllog',
                    name='call',
                    field=models.ForeignKey(blank=True, to='core.Call',
                                            null=True),
                ),
            ]
        ),
    ]
