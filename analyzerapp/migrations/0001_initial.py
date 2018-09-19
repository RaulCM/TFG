# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('identifier', models.CharField(max_length=150, default='Null')),
                ('full_name', models.TextField(default='Null')),
                ('description', models.TextField(default='Null')),
                ('html_url', models.URLField(max_length=350, default='Null')),
            ],
        ),
    ]
