# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
import core

class Migration(migrations.Migration):

    replaces = [('core', '0001_initial'), ('core', '0003_auto_20151130_1219'), ('core', '0004_auto_20151130_1356'), ('core', '0005_auto_20151130_1449'), ('core', '0006_auto_20151130_1756'), ('core', '0007_remove_outofserviceperiod_shift_unit'), ('core', '0008_auto_20151130_2311')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InCallPeriod',
            fields=[
                ('in_call_id', models.IntegerField(primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
            options={
                'managed': False,
                'db_table': 'in_call',
            },
        ),
        migrations.CreateModel(
            name='OfficerActivity',
            fields=[
                ('officer_activity_id', models.IntegerField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(db_column='time_')),
            ],
            options={
                'managed': False,
                'db_table': 'discrete_officer_activity',
            },
        ),
        migrations.CreateModel(
            name='Beat',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('beat_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'beat',
            },
        ),
        migrations.CreateModel(
            name='Bureau',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('bureau_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'bureau',
            },
        ),
        migrations.CreateModel(
            name='Call',
            fields=[
                ('call_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('time_received', models.DateTimeField(db_index=True)),
                ('time_routed', models.DateTimeField(null=True, blank=True)),
                ('time_finished', models.DateTimeField(null=True, blank=True)),
                ('year_received', models.IntegerField(db_index=True)),
                ('month_received', models.IntegerField(db_index=True)),
                ('week_received', models.IntegerField(db_index=True)),
                ('dow_received', models.IntegerField(db_index=True)),
                ('hour_received', models.IntegerField(db_index=True)),
                ('case_id', models.BigIntegerField(null=True, blank=True)),
                ('street_num', models.IntegerField(null=True, blank=True)),
                ('street_name', models.TextField(null=True, blank=True)),
                ('crossroad1', models.TextField(null=True, blank=True)),
                ('crossroad2', models.TextField(null=True, blank=True)),
                ('geox', models.FloatField(null=True, blank=True)),
                ('geoy', models.FloatField(null=True, blank=True)),
                ('business', models.TextField(null=True, blank=True)),
                ('report_only', models.BooleanField()),
                ('cancelled', models.BooleanField(db_index=True)),
                ('first_unit_dispatch', models.DateTimeField(null=True, blank=True)),
                ('first_unit_enroute', models.DateTimeField(null=True, blank=True)),
                ('first_unit_arrive', models.DateTimeField(null=True, blank=True)),
                ('first_unit_transport', models.DateTimeField(null=True, blank=True)),
                ('last_unit_clear', models.DateTimeField(null=True, blank=True)),
                ('time_closed', models.DateTimeField(null=True, blank=True)),
                ('close_comments', models.TextField(null=True, blank=True)),
                ('officer_response_time', models.DurationField(null=True, blank=True)),
                ('overall_response_time', models.DurationField(null=True, blank=True)),
            ],
            options={
                'db_table': 'call',
            },
        ),
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('call_log_id', models.AutoField(primary_key=True, serialize=False)),
                ('time_recorded', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'call_log',
            },
        ),
        migrations.CreateModel(
            name='CallSource',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('call_source_id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(default=None, unique=True, max_length=10)),
            ],
            options={
                'db_table': 'call_source',
            },
        ),
        migrations.CreateModel(
            name='CallUnit',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('call_unit_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'call_unit',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('city_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'city',
            },
        ),
        migrations.CreateModel(
            name='CloseCode',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('close_code_id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(default=None, unique=True, max_length=10)),
            ],
            options={
                'db_table': 'close_code',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('district_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'district',
            },
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('division_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'division',
            },
        ),
        migrations.CreateModel(
            name='Nature',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('nature_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'nature',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('note_id', models.AutoField(primary_key=True, serialize=False)),
                ('body', models.TextField(null=True, blank=True)),
                ('time_recorded', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'db_table': 'note',
            },
        ),
        migrations.CreateModel(
            name='NoteAuthor',
            fields=[
                ('note_author_id', models.AutoField(primary_key=True, serialize=False)),
                ('descr', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'note_author',
            },
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('officer_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(null=True, blank=True)),
                ('name_aka', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'officer',
            },
        ),
        migrations.CreateModel(
            name='OfficerActivityType',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('officer_activity_type_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'officer_activity_type',
            },
        ),
        migrations.CreateModel(
            name='OOSCode',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('oos_code_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'oos_code',
            },
        ),
        migrations.CreateModel(
            name='OutOfServicePeriod',
            fields=[
                ('oos_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.TextField(null=True, blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('duration', models.DurationField(null=True, blank=True)),
                ('call_unit', models.ForeignKey(blank=True, related_name='+', null=True, to='core.CallUnit', db_column='call_unit_id')),
                ('oos_code', models.ForeignKey(blank=True, related_name='+', null=True, to='core.OOSCode', db_column='oos_code_id')),
            ],
            options={
                'db_table': 'out_of_service',
            },
        ),
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('priority_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'priority',
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('sector_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'sector',
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('shift_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'shift',
            },
        ),
        migrations.CreateModel(
            name='ShiftUnit',
            fields=[
                ('shift_unit_id', models.AutoField(primary_key=True, serialize=False)),
                ('in_time', models.DateTimeField(null=True, blank=True)),
                ('out_time', models.DateTimeField(null=True, blank=True)),
                ('bureau', models.ForeignKey(blank=True, related_name='+', null=True, to='core.Bureau', db_column='bureau_id')),
                ('call_unit', models.ForeignKey(blank=True, related_name='+', null=True, to='core.CallUnit', db_column='call_unit_id')),
                ('division', models.ForeignKey(blank=True, related_name='+', null=True, to='core.Division', db_column='division_id')),
                ('officer', models.ForeignKey(blank=True, related_name='+', null=True, to='core.Officer', db_column='officer_id')),
                ('shift', models.ForeignKey(blank=True, related_name='+', null=True, to='core.Shift', db_column='shift_id')),
            ],
            options={
                'db_table': 'shift_unit',
            },
        ),
        migrations.CreateModel(
            name='Squad',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('squad_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'squad',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('transaction_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'transaction',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('unit_id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(default=None, unique=True, max_length=10)),
            ],
            options={
                'db_table': 'unit',
            },
        ),
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('zip_code_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'zip_code',
            },
        ),
        migrations.AddField(
            model_name='shiftunit',
            name='unit',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.Unit', db_column='unit_id'),
        ),
        migrations.AddField(
            model_name='note',
            name='call',
            field=models.ForeignKey(blank=True, to='core.Call', null=True),
        ),
        migrations.AddField(
            model_name='note',
            name='note_author',
            field=models.ForeignKey(blank=True, to='core.NoteAuthor', null=True),
        ),
        migrations.AddField(
            model_name='district',
            name='sector',
            field=models.ForeignKey(blank=True, to='core.Sector', null=True),
        ),
        migrations.AddField(
            model_name='callunit',
            name='squad',
            field=models.ForeignKey(blank=True, related_name='squad', null=True, to='core.Squad', db_column='squad_id'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='call',
            field=models.ForeignKey(blank=True, to='core.Call', null=True),
        ),
        migrations.AddField(
            model_name='calllog',
            name='call_unit',
            field=models.ForeignKey(blank=True, to='core.CallUnit', null=True),
        ),
        migrations.AddField(
            model_name='calllog',
            name='close_code',
            field=models.ForeignKey(blank=True, to='core.CloseCode', null=True),
        ),
        migrations.AddField(
            model_name='calllog',
            name='shift',
            field=models.ForeignKey(blank=True, to='core.Shift', null=True),
        ),
        migrations.AddField(
            model_name='calllog',
            name='transaction',
            field=models.ForeignKey(blank=True, to='core.Transaction', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='beat',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.Beat'),
        ),
        migrations.AddField(
            model_name='call',
            name='call_source',
            field=models.ForeignKey(blank=True, to='core.CallSource', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='city',
            field=models.ForeignKey(blank=True, to='core.City', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='close_code',
            field=models.ForeignKey(blank=True, to='core.CloseCode', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='district',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.District'),
        ),
        migrations.AddField(
            model_name='call',
            name='first_dispatched',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='call',
            name='nature',
            field=models.ForeignKey(blank=True, to='core.Nature', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='primary_unit',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='call',
            name='priority',
            field=models.ForeignKey(blank=True, to='core.Priority', null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='reporting_unit',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='call',
            name='sector',
            field=models.ForeignKey(blank=True, related_name='+', null=True, to='core.Sector'),
        ),
        migrations.AddField(
            model_name='call',
            name='zip_code',
            field=models.ForeignKey(blank=True, to='core.ZipCode', null=True),
        ),
        migrations.AddField(
            model_name='beat',
            name='district',
            field=models.ForeignKey(blank=True, to='core.District', null=True),
        ),
        migrations.AddField(
            model_name='beat',
            name='sector',
            field=models.ForeignKey(blank=True, to='core.Sector', null=True),
        ),
        migrations.AddField(
            model_name='bureau',
            name='code',
            field=models.CharField(default=None, unique=True, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='division',
            name='code',
            field=models.CharField(default=None, unique=True, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ooscode',
            name='code',
            field=models.CharField(default=None, unique=True, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='officer',
            name='name',
            field=models.CharField(default='', max_length=255, blank=True),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='officer',
            name='name_aka',
        ),
        migrations.AddField(
            model_name='officer',
            name='name_aka',
            field=django.contrib.postgres.fields.ArrayField(default=[], size=None, base_field=models.CharField(max_length=255), blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outofserviceperiod',
            name='shift',
            field=models.ForeignKey(blank=True, to='core.Shift', null=True),
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['code']},
        ),
        migrations.AddField(
            model_name='transaction',
            name='code',
            field=models.CharField(default=None, unique=True, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='descr',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.CreateModel(
            name='NatureGroup',
            fields=[
                ('descr', models.TextField(verbose_name='Description', unique=True)),
                ('nature_group_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'nature_group',
            },
        ),
        migrations.AddField(
            model_name='nature',
            name='nature_group',
            field=models.ForeignKey(blank=True, to='core.NatureGroup', null=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_arrive',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_dispatch',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_enroute',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='first_unit_transport',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='last_unit_clear',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_closed',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_finished',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_received',
            field=core.models.DateTimeNoTZField(db_index=True),
        ),
        migrations.AlterField(
            model_name='call',
            name='time_routed',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calllog',
            name='time_recorded',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='time_recorded',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='outofserviceperiod',
            name='end_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='outofserviceperiod',
            name='start_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shiftunit',
            name='in_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='shiftunit',
            name='out_time',
            field=core.models.DateTimeNoTZField(null=True, blank=True),
        ),
    ]
