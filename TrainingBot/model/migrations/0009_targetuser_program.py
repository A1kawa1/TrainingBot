# Generated by Django 3.2 on 2023-03-05 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0008_auto_20230305_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetuser',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='model.userprogram'),
        ),
    ]
