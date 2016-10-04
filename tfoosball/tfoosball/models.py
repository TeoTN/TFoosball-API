from django.db import models
from django.contrib.auth.models import AbstractUser


class Player(AbstractUser):
    exp = models.IntegerField(blank=False, null=False, default=1000)
    att_ratio = models.FloatField(default=0.0, db_column='att')
    def_ratio = models.FloatField(default=0.0, db_column='def')
    win_ratio = models.FloatField(default=0.0, db_column='win')
    win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    lowest_exp = models.IntegerField(default=1000)
    highest_exp = models.IntegerField(default=1000)


class Match(models.Model):
    red_att = models.ForeignKey(Player, related_name='red_att')
    red_def = models.ForeignKey(Player, related_name='red_def')
    blue_att = models.ForeignKey(Player, related_name='blue_att')
    blue_def = models.ForeignKey(Player, related_name='blue_def')
    date = models.DateTimeField(auto_now_add=True, blank=True)
    red_score = models.IntegerField()
    blue_score = models.IntegerField()
    points = models.IntegerField()
