# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_update_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='callunit',
            name='beat',
            field=models.ForeignKey(blank=True, to='core.Beat', related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='callunit',
            name='district',
            field=models.ForeignKey(blank=True, to='core.District', related_name='+', null=True),
        ),
        migrations.AlterField(
            model_name='callunit',
            name='squad',
            field=models.ForeignKey(blank=True, to='core.Squad', related_name='squad', null=True),
        ),
    ]
