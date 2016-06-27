# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_siteconfiguration'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OfficerActivityType',
        ),
        migrations.DeleteModel(
            name='OutOfServicePeriod',
        ),
        migrations.DeleteModel(
            name='OOSCode',
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='department_abbr',
            field=models.CharField(default='CPD', verbose_name='Department abbreviation', max_length=10),
        ),
    ]
