# Generated by Django 3.2 on 2023-02-14 17:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0002_userdayfood'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdayfood',
            name='time',
            field=models.TimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
