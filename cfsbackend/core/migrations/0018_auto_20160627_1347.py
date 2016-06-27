# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20160627_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='call',
        ),
        migrations.RemoveField(
            model_name='note',
            name='note_author',
        ),
        migrations.DeleteModel(
            name='Note',
        ),
        migrations.DeleteModel(
            name='NoteAuthor',
        ),
    ]
