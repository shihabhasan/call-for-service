# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20151204_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='beat',
            field=models.ForeignKey(blank=True, to='core.Beat', null=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='district',
            field=models.ForeignKey(blank=True, to='core.District', null=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='sector',
            field=models.ForeignKey(blank=True, to='core.Sector', null=True),
        ),
    ]
