# Generated by Django 3.1.3 on 2020-11-03 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzerapp', '0004_repository_fork_api_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='default_branch',
            field=models.TextField(default='Null'),
        ),
    ]
