# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20160628_1045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='call',
            name='zip_code',
        ),
        migrations.DeleteModel(
            name='ZipCode',
        ),
        migrations.RenameField(
            model_name='call',
            old_name='zip_code_str',
            new_name='zip_code',
        ),
    ]
