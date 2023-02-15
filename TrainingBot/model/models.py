# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import uuid


class Food(models.Model):
    name = models.TextField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)


class Guide(models.Model):
    advice = models.TextField(blank=True, null=True)
    question = models.TextField(blank=True, null=True)
    answer1 = models.IntegerField(blank=True, null=True)
    answer2 = models.IntegerField(blank=True, null=True)


class InfoUser(models.Model):
    age = models.IntegerField(blank=True, null=True, default=0)
    height = models.IntegerField(blank=True, null=True, default=0)
    gender = models.TextField(blank=True, null=True, default='None')
    ideal_weight = models.TextField(blank=True, null=True, default=0)
    user = models.ForeignKey('User', models.CASCADE, related_name='info')


class TargetUser(models.Model):
    type = models.TextField(blank=True, null=True, default='None')
    activity = models.TextField(blank=True, null=True, default='None')
    period = models.IntegerField(blank=True, null=True, default=0)
    cur_week = models.IntegerField(blank=True, null=True, default=0)
    cur_week_noraml_dci = models.IntegerField(blank=True, null=True, default=0)
    dci = models.IntegerField(blank=True, null=True, default=0)
    cur_dci = models.IntegerField(blank=True, null=True, default=0)
    cur_weight = models.IntegerField(blank=True, null=True, default=0)
    target_weight = models.IntegerField(blank=True, null=True, default=0)
    user = models.ForeignKey('User', models.CASCADE, related_name='target')
    programm_ready = models.BooleanField(blank=True, null=True)


class User(models.Model):
    id = models.IntegerField(unique=True, blank=False, primary_key=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class UserFood(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='food')
    food = models.ForeignKey(Food, models.CASCADE, related_name='food')


class UserStageGuide(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='stage')
    stage = models.IntegerField(blank=True, null=True, default=0)
    question = models.IntegerField(blank=True, null=True, default=1)


class UserDayFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='day_food')
    name = models.TextField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField()


class ResultDayDci(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='result_day_dci')
    time = models.DateTimeField()
    calories = models.IntegerField(default=0)