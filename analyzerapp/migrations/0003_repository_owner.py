# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzerapp', '0002_auto_20180919_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='owner',
            field=models.TextField(default='Null'),
        ),
    ]
