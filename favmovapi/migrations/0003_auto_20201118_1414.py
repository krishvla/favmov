# Generated by Django 3.1.3 on 2020-11-18 08:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('favmovapi', '0002_auto_20201117_2249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collections',
            old_name='id',
            new_name='uuid',
        ),
        migrations.AddField(
            model_name='collections',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
