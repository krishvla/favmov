# Generated by Django 3.1.3 on 2020-11-18 08:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('favmovapi', '0003_auto_20201118_1414'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movies',
            old_name='api_uuid',
            new_name='uuid',
        ),
    ]
