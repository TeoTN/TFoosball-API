from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
import logging
logger = logging.getLogger('tfoosball.matches')


class Player(AbstractUser):
    exp = models.IntegerField(blank=False, null=False, default=1000)
    offence = models.IntegerField(default=0)
    defence = models.IntegerField(default=0)
    played = models.IntegerField(default=0) 
    win_streak = models.IntegerField(default=0)
    curr_win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    curr_lose_streak = models.IntegerField(default=0)
    lowest_exp = models.IntegerField(default=1000)
    highest_exp = models.IntegerField(default=1000)

    @property
    def won(self):
        return self.offence + self.defence

    @property
    def lost(self):
        return self.played - self.won

    @property
    def att_ratio(self):
        return round(self.offence / self.won if self.won > 0 else 0, 2)

    @property
    def def_ratio(self):
        return round(self.defence / self.won if self.won > 0 else 0, 2)
    
    @property
    def win_ratio(self):
        return round(self.won / self.played if self.played > 0 else 0, 2)

    def update_extremes(self):
        self.win_streak = max(self.curr_win_streak, self.win_streak)
        self.lose_streak = max(self.curr_lose_streak, self.lose_streak)
        self.lowest_exp = min(self.lowest_exp, self.exp)
        self.highest_exp = max(self.highest_exp, self.exp)

    def after_match_update(self, points, is_winner, is_offence):
        self.exp += points
        self.played += 1

        if is_winner:
            self.curr_win_streak += 1
            self.curr_lose_streak = 0 

            if is_offence:
                self.offence += 1 
            else:
                self.defence += 1
        else:
            self.curr_win_streak = 0 
            self.curr_lose_streak += 1

        self.update_extremes()

        self.save()

    def get_latest_matches(self, number=7):
        return Match.objects.all().filter(Q(red_att=self.id)|Q(red_def=self.id)|Q(blue_att=self.id)|Q(blue_def=self.id)).order_by('-date')[:int(number)]


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
        :return: The amount of points that red team should gain and information whether read team won
        """
        K = int(self.status)
        G = (11+abs(self.red_score - self.blue_score)) / 8
        dr = ((self.red_att.exp + self.red_def.exp) - (self.blue_att.exp + self.blue_def.exp))
        We = 1 / ((10 ** -(dr/400))+1)
        W = 1 if self.red_score > self.blue_score else 0
        logger.debug('Params r: {0} b: {1} K: {2} G: {3} dr: {4} We: {5} W: {6} score={7}'.format(
            self.red_score, self.blue_score, K, G, dr, We, W, int(K*G*(W-We))
        ))
        return (int(K*G*(W-We)), self.red_score > self.blue_score)
 
    def save(self, *args, **kwargs):
        logger.debug('Adding match')
        self.points, is_red_winner = self.calculate_points()
        self.red_att.after_match_update(self.points, is_red_winner, True)
        self.red_def.after_match_update(self.points, is_red_winner, False)
        self.blue_att.after_match_update(-self.points, not is_red_winner, True)
        self.blue_def.after_match_update(-self.points, not is_red_winner, False)

        super(Match, self).save(*args, **kwargs)


class ExpHistory(models.Model):
    player = models.ForeignKey(Player, related_name='exp_history')
    date = models.DateField(auto_now_add=True, blank=True)
    exp = models.IntegerField()
