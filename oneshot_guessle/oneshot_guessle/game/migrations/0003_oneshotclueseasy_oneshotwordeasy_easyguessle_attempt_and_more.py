# Generated by Django 4.0.9 on 2023-05-10 17:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OneshotCluesEasy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clue1', models.CharField(max_length=5)),
                ('clue2', models.CharField(max_length=5)),
                ('clue3', models.CharField(max_length=5)),
                ('clue4', models.CharField(max_length=5)),
                ('clue5', models.CharField(max_length=5)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Easy Clue',
                'verbose_name_plural': 'Easy Clues',
            },
        ),
        migrations.CreateModel(
            name='OneshotWordEasy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=5)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('correctAnswers', models.PositiveIntegerField(default=0)),
                ('clues', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.oneshotclues')),
            ],
            options={
                'verbose_name': 'Oneshot Easy Daily Word',
                'verbose_name_plural': 'Oneshot Easy Daily Words',
            },
        ),
        migrations.CreateModel(
            name='EasyGuessle_Attempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guess', models.CharField(max_length=5)),
                ('date', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.oneshotword')),
            ],
            options={
                'verbose_name': 'Easy Word Attempt',
                'verbose_name_plural': 'Easy Word Attempts',
            },
        ),
        migrations.CreateModel(
            name='Daily_Stars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True, null=True)),
                ('stars', models.PositiveBigIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Daily Star Count',
                'verbose_name_plural': 'Daily Stars',
            },
        ),
    ]
