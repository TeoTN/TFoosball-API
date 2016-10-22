from django.db import models
from django.contrib.auth.models import AbstractUser
import logging
logger = logging.getLogger('tfoosball.matches')


class Player(AbstractUser):
    exp = models.IntegerField(blank=False, null=False, default=1000)
    att_ratio = models.FloatField(default=0.0, db_column='att')
    def_ratio = models.FloatField(default=0.0, db_column='def')
    win_ratio = models.FloatField(default=0.0, db_column='win')
    win_streak = models.IntegerField(default=0)
    curr_win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    curr_lose_streak = models.IntegerField(default=0)
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
    status = models.IntegerField(default=20)

    def calculate_points(self):
        """
        :return: The amount of points that red team should gain
        """
        logger.debug('Adding match')
        K = int(self.status)
        G = (11+abs(self.red_score - self.blue_score)) / 8
        dr = ((self.red_att.exp + self.red_def.exp) - (self.blue_att.exp + self.red_att.exp))
        We = 1 / ((10 ** -(dr/400))+1)
        W = 1 if self.red_score > self.blue_score else 0
        logger.debug('Params r: {0} b: {1} K: {2} G: {3} dr: {4} We: {5} W: {6} score={7}'.format(
            self.red_score, self.blue_score, K, G, dr, We, W, int(K*G*(W-We))
        ))
        return int(K*G*(W-We))

    def save(self, *args, **kwargs):
        self.points = self.calculate_points()
        self.red_att.exp += self.points
        self.red_att.save()
        self.red_def.exp += self.points
        self.red_def.save()
        self.blue_att.exp -= self.points
        self.blue_att.save()
        self.blue_def.exp -= self.points
        self.blue_def.save()
        super(Match, self).save(*args, **kwargs)
