# Generated by Django 5.1.4 on 2025-02-19 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='create_at',
        ),
    ]
