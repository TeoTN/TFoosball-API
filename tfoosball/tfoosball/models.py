from django.db import models
from django.contrib.auth.models import AbstractUser


class Player(AbstractUser):
    exp = models.IntegerField(blank=False, null=False, default=1000)
    att_ratio = models.FloatField(default=0.0, db_column='att')
    def_ratio = models.FloatField(default=0.0, db_column='def')
    win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    lowest_exp = models.IntegerField(default=1000)
    highest_exp = models.IntegerField(default=1000)
