# Generated by Django 4.0.9 on 2023-04-23 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_alter_word_lastoccurance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='lastOccurance',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
