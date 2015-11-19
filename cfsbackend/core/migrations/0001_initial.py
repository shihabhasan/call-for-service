# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InCallPeriod',
            fields=[
                ('in_call_id', models.IntegerField(serialize=False, primary_key=True)),
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
                ('officer_activity_id', models.IntegerField(serialize=False, primary_key=True)),
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
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('beat_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'beat',
            },
        ),
        migrations.CreateModel(
            name='Bureau',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('bureau_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'bureau',
            },
        ),
        migrations.CreateModel(
            name='Call',
            fields=[
                ('call_id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('time_received', models.DateTimeField(db_index=True)),
                ('time_routed', models.DateTimeField(blank=True, null=True)),
                ('time_finished', models.DateTimeField(blank=True, null=True)),
                ('year_received', models.IntegerField(db_index=True)),
                ('month_received', models.IntegerField(db_index=True)),
                ('week_received', models.IntegerField(db_index=True)),
                ('dow_received', models.IntegerField(db_index=True)),
                ('hour_received', models.IntegerField(db_index=True)),
                ('case_id', models.BigIntegerField(blank=True, null=True)),
                ('street_num', models.IntegerField(blank=True, null=True)),
                ('street_name', models.TextField(blank=True, null=True)),
                ('crossroad1', models.TextField(blank=True, null=True)),
                ('crossroad2', models.TextField(blank=True, null=True)),
                ('geox', models.FloatField(blank=True, null=True)),
                ('geoy', models.FloatField(blank=True, null=True)),
                ('business', models.TextField(blank=True, null=True)),
                ('report_only', models.BooleanField()),
                ('cancelled', models.BooleanField(db_index=True)),
                ('first_unit_dispatch', models.DateTimeField(blank=True, null=True)),
                ('first_unit_enroute', models.DateTimeField(blank=True, null=True)),
                ('first_unit_arrive', models.DateTimeField(blank=True, null=True)),
                ('first_unit_transport', models.DateTimeField(blank=True, null=True)),
                ('last_unit_clear', models.DateTimeField(blank=True, null=True)),
                ('time_closed', models.DateTimeField(blank=True, null=True)),
                ('close_comments', models.TextField(blank=True, null=True)),
                ('officer_response_time', models.DurationField(blank=True, null=True)),
                ('overall_response_time', models.DurationField(blank=True, null=True)),
            ],
            options={
                'db_table': 'call',
            },
        ),
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('call_log_id', models.AutoField(serialize=False, primary_key=True)),
                ('time_recorded', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'call_log',
            },
        ),
        migrations.CreateModel(
            name='CallSource',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('call_source_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'call_source',
            },
        ),
        migrations.CreateModel(
            name='CallUnit',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('call_unit_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'call_unit',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('city_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'city',
            },
        ),
        migrations.CreateModel(
            name='CloseCode',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('close_code_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'close_code',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('district_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'district',
            },
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('division_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'division',
            },
        ),
        migrations.CreateModel(
            name='Nature',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('nature_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'nature',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('note_id', models.AutoField(serialize=False, primary_key=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('time_recorded', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'note',
            },
        ),
        migrations.CreateModel(
            name='NoteAuthor',
            fields=[
                ('note_author_id', models.AutoField(serialize=False, primary_key=True)),
                ('descr', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'note_author',
            },
        ),
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('officer_id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('name_aka', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'officer',
            },
        ),
        migrations.CreateModel(
            name='OfficerActivityType',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('officer_activity_type_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'officer_activity_type',
            },
        ),
        migrations.CreateModel(
            name='OOSCode',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('oos_code_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'oos_code',
            },
        ),
        migrations.CreateModel(
            name='OutOfServicePeriod',
            fields=[
                ('oos_id', models.AutoField(serialize=False, primary_key=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('call_unit', models.ForeignKey(blank=True, db_column='call_unit_id', null=True, related_name='+', to='core.CallUnit')),
                ('oos_code', models.ForeignKey(blank=True, db_column='oos_code_id', null=True, related_name='+', to='core.OOSCode')),
            ],
            options={
                'db_table': 'out_of_service',
            },
        ),
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('priority_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'priority',
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('sector_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'sector',
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('shift_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'shift',
            },
        ),
        migrations.CreateModel(
            name='ShiftUnit',
            fields=[
                ('shift_unit_id', models.AutoField(serialize=False, primary_key=True)),
                ('in_time', models.DateTimeField(blank=True, null=True)),
                ('out_time', models.DateTimeField(blank=True, null=True)),
                ('bureau', models.ForeignKey(blank=True, db_column='bureau_id', null=True, related_name='+', to='core.Bureau')),
                ('call_unit', models.ForeignKey(blank=True, db_column='call_unit_id', null=True, related_name='+', to='core.CallUnit')),
                ('division', models.ForeignKey(blank=True, db_column='division_id', null=True, related_name='+', to='core.Division')),
                ('officer', models.ForeignKey(blank=True, db_column='officer_id', null=True, related_name='+', to='core.Officer')),
                ('shift', models.ForeignKey(blank=True, db_column='shift_id', null=True, related_name='+', to='core.Shift')),
            ],
            options={
                'db_table': 'shift_unit',
            },
        ),
        migrations.CreateModel(
            name='Squad',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('squad_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'squad',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('transaction_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'transaction',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('unit_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'unit',
            },
        ),
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('descr', models.TextField(unique=True, verbose_name='Description')),
                ('zip_code_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'zip_code',
            },
        ),
        migrations.CreateModel(
            name='CallGeneralCategory',
            fields=[
                ('call_id', models.OneToOneField(serialize=False, related_name='categories', to='core.Call', primary_key=True)),
                ('gun_related', models.BooleanField()),
                ('gang_related', models.BooleanField()),
                ('spanish_related', models.BooleanField()),
                ('mental_illness_related', models.BooleanField()),
                ('homeless_related', models.BooleanField()),
                ('officer_citizen_conflict', models.BooleanField()),
            ],
            options={
                'managed': False,
                'db_table': 'call_general_category',
            },
        ),
        migrations.AddField(
            model_name='shiftunit',
            name='unit',
            field=models.ForeignKey(blank=True, db_column='unit_id', null=True, related_name='+', to='core.Unit'),
        ),
        migrations.AddField(
            model_name='outofserviceperiod',
            name='shift_unit_id',
            field=models.ForeignKey(blank=True, null=True, to='core.ShiftUnit'),
        ),
        migrations.AddField(
            model_name='note',
            name='call',
            field=models.ForeignKey(blank=True, null=True, to='core.Call'),
        ),
        migrations.AddField(
            model_name='note',
            name='note_author',
            field=models.ForeignKey(blank=True, null=True, to='core.NoteAuthor'),
        ),
        migrations.AddField(
            model_name='district',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, to='core.Sector'),
        ),
        migrations.AddField(
            model_name='callunit',
            name='squad',
            field=models.ForeignKey(blank=True, db_column='squad_id', null=True, related_name='squad', to='core.Squad'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='call',
            field=models.ForeignKey(blank=True, null=True, to='core.Call'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='call_unit',
            field=models.ForeignKey(blank=True, null=True, to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='close_code',
            field=models.ForeignKey(blank=True, null=True, to='core.CloseCode'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='shift',
            field=models.ForeignKey(blank=True, null=True, to='core.Shift'),
        ),
        migrations.AddField(
            model_name='calllog',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, to='core.Transaction'),
        ),
        migrations.AddField(
            model_name='call',
            name='beat',
            field=models.ForeignKey(blank=True, null=True, related_name='+', to='core.Beat'),
        ),
        migrations.AddField(
            model_name='call',
            name='call_source',
            field=models.ForeignKey(blank=True, null=True, to='core.CallSource'),
        ),
        migrations.AddField(
            model_name='call',
            name='city',
            field=models.ForeignKey(blank=True, null=True, to='core.City'),
        ),
        migrations.AddField(
            model_name='call',
            name='close_code',
            field=models.ForeignKey(blank=True, null=True, to='core.CloseCode'),
        ),
        migrations.AddField(
            model_name='call',
            name='district',
            field=models.ForeignKey(blank=True, null=True, related_name='+', to='core.District'),
        ),
        migrations.AddField(
            model_name='call',
            name='first_dispatched',
            field=models.ForeignKey(blank=True, null=True, related_name='+', to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='call',
            name='nature',
            field=models.ForeignKey(blank=True, null=True, to='core.Nature'),
        ),
        migrations.AddField(
            model_name='call',
            name='primary_unit',
            field=models.ForeignKey(blank=True, null=True, related_name='+', to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='call',
            name='priority',
            field=models.ForeignKey(blank=True, null=True, to='core.Priority'),
        ),
        migrations.AddField(
            model_name='call',
            name='reporting_unit',
            field=models.ForeignKey(blank=True, null=True, related_name='+', to='core.CallUnit'),
        ),
        migrations.AddField(
            model_name='call',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, related_name='+', to='core.Sector'),
        ),
        migrations.AddField(
            model_name='call',
            name='zip_code',
            field=models.ForeignKey(blank=True, null=True, to='core.ZipCode'),
        ),
        migrations.AddField(
            model_name='beat',
            name='district',
            field=models.ForeignKey(blank=True, null=True, to='core.District'),
        ),
        migrations.AddField(
            model_name='beat',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, to='core.Sector'),
        ),
    ]
