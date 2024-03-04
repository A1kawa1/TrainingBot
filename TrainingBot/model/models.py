from django.db import models
from datetime import datetime
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
    ideal_weight = models.IntegerField(blank=True, null=True, default=0)
    user = models.ForeignKey('User', models.CASCADE, related_name='info')


class TargetUser(models.Model):
    type = models.TextField(blank=True, null=True, default='None')
    activity = models.TextField(blank=True, null=True, default='None')
    dci = models.IntegerField(blank=True, null=True, default=0)
    cur_dci = models.IntegerField(blank=True, null=True, default=0)
    cur_weight = models.FloatField(blank=True, null=True, default=0)
    target_weight = models.FloatField(blank=True, null=True, default=0)
    percentage_decrease = models.IntegerField(default=15)
    user = models.ForeignKey('User', models.CASCADE, related_name='target')
    program = models.ForeignKey('UserProgram', models.SET_NULL, null=True)
    achieved = models.BooleanField(default=False)


class User(models.Model):
    id = models.IntegerField(unique=True, blank=False, primary_key=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    datetime_start = models.DateTimeField()


class UserFood(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='food')
    food = models.ForeignKey(Food, models.CASCADE, related_name='food')


class UserStageGuide(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='stage')
    stage = models.IntegerField(blank=True, null=True, default=-1)
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
    cur_weight = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super(ResultDayDci, self).save(*args, **kwargs)
        stage = UserStageGuide.objects.get(user=self.user).stage
        if stage == 5:
            time_zon = self.user.datetime_start.astimezone().tzinfo
            cur_date = datetime.now(time_zon).date()

            result_day_dci = self.user.result_day_dci.filter(
                ~models.Q(cur_weight=None))

            if len(result_day_dci) == 0:
                dif_date = (
                    cur_date - self.user.program.last().date_start).days
            else:
                dif_date = (cur_date - result_day_dci.last().date).days
            dif_date = dif_date % 7 if dif_date != 0 else 1
            remind = self.user.remind.last()
            remind.day_without_indication_weight = dif_date
            remind.save()


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
    cur_weight = models.FloatField(blank=True, null=True, default=0)
    achievement = models.IntegerField(blank=True, null=True, default=0)


class Message(models.Model):
    mesKey = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    message = models.TextField()


class RemindUser(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='remind')
    remind_first = models.BooleanField(default=True)
    remind_second = models.BooleanField(default=True)
    day_without_indication_weight = models.PositiveIntegerField(default=1)
    remind_weight = models.BooleanField(default=True)
