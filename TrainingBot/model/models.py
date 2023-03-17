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
    dci = models.IntegerField(blank=True, null=True, default=0)
    cur_dci = models.IntegerField(blank=True, null=True, default=0)
    cur_weight = models.IntegerField(blank=True, null=True, default=0)
    target_weight = models.IntegerField(blank=True, null=True, default=0)
    percentage_decrease = models.IntegerField(default=15)
    user = models.ForeignKey('User', models.CASCADE, related_name='target')
    program = models.ForeignKey('UserProgram', models.SET_NULL, null=True)


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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='day_food')
    name = models.TextField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    time = models.DateTimeField()


class ResultDayDci(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='result_day_dci')
    date = models.DateField()
    calories = models.IntegerField(default=0)
    deficit = models.IntegerField(blank=True, null=True)
    cur_weight = models.IntegerField(blank=True, null=True)


class UserProgram(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='program'
    )
    date_start = models.DateField()
    start_dci = models.IntegerField(blank=True, null=True, default=0)
    cur_dci = models.IntegerField(blank=True, null=True, default=0)
    phase1 = models.IntegerField(blank=True, null=True, default=0)
    phase2 = models.IntegerField(blank=True, null=True, default=0)
    cur_day = models.IntegerField(blank=True, null=True, default=0)
    cur_weight = models.IntegerField(blank=True, null=True, default=0)
    achievement = models.IntegerField(blank=True, null=True, default=0)
