# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20160628_1057'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='priority',
            options={'verbose_name_plural': 'priorities', 'ordering': ('sort_order',)},
        ),
        migrations.AddField(
            model_name='priority',
            name='sort_order',
            field=models.PositiveIntegerField(editable=False, default=0, db_index=True),
        ),
    ]
