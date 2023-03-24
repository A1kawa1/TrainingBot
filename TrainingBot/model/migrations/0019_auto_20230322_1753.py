# Generated by Django 3.2 on 2023-03-22 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0018_message_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='datetime_start',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='RemindUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remind_first', models.BooleanField(default=False)),
                ('remind_second', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remind', to='model.user')),
            ],
        ),
    ]
