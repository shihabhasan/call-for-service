# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160621_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='InCallPeriod',
            fields=[
                ('in_call_id', models.IntegerField(serialize=False, primary_key=True)),
                ('start_time', core.models.DateTimeNoTZField()),
                ('end_time', core.models.DateTimeNoTZField()),
            ],
            options={
                'db_table': 'in_call',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OfficerActivity',
            fields=[
                ('officer_activity_id', models.IntegerField(serialize=False, primary_key=True, db_column='discrete_officer_activity_id')),
                ('time', core.models.DateTimeNoTZField(db_column='time_')),
            ],
            options={
                'db_table': 'discrete_officer_activity',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OfficerActivityType',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('officer_activity_type_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'officer_activity_type',
            },
        ),
        migrations.CreateModel(
            name='OOSCode',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('oos_code_id', models.AutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=10)),
            ],
            options={
                'db_table': 'oos_code',
            },
        ),
        migrations.CreateModel(
            name='OutOfServicePeriod',
            fields=[
                ('oos_id', models.AutoField(serialize=False, primary_key=True)),
                ('location', models.TextField(null=True, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('start_time', core.models.DateTimeNoTZField(null=True, blank=True)),
                ('end_time', core.models.DateTimeNoTZField(null=True, blank=True)),
                ('duration', models.DurationField(null=True, blank=True)),
                ('call_unit', models.ForeignKey(blank=True, to='core.CallUnit', null=True, related_name='+', db_column='call_unit_id')),
                ('oos_code', models.ForeignKey(blank=True, to='officer_allocation.OOSCode', null=True, related_name='+', db_column='oos_code_id')),
                ('shift', models.ForeignKey(blank=True, to='core.Shift', null=True)),
            ],
            options={
                'db_table': 'out_of_service',
            },
        ),
    ]
