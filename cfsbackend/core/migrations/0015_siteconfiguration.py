# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20151208_1039'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('department_name', models.CharField(default='City Police Department', max_length=255)),
                ('department_abbr', models.CharField(default='CPD', max_length=10)),
                ('maintenance_mode', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Site Configuration',
            },
        ),
    ]
