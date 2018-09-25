# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzerapp', '0003_repository_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='name',
            field=models.TextField(default='Null'),
        ),
    ]
