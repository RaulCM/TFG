# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzerapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repository',
            name='id',
        ),
        migrations.AlterField(
            model_name='repository',
            name='identifier',
            field=models.CharField(primary_key=True, max_length=150, serialize=False, default='Null'),
        ),
    ]
