# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzerapp', '0004_repository_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Errors',
            fields=[
                ('error_id', models.CharField(primary_key=True, max_length=150, serialize=False, default='Null')),
                ('count', models.IntegerField(default=0)),
            ],
        ),
    ]
