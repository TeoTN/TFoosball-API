from django.db import models
from django.db.models import Q, F, Case, When, Func, ExpressionWrapper
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class Round(Func):
    function = 'ROUND'
    arity = 1
    template = '%(function)s(%(expressions)s, %(place)d)'


class Team(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    name = models.CharField(max_length=32, unique=True)
    domain = models.CharField(max_length=32, unique=True, validators=[alphanumeric])

    def __str__(self):
        return self.name


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
    hidden = models.BooleanField(default=False)

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

    def get_latest_matches(self):
        return Match.objects.all() \
            .filter(Q(red_att=self.id) | Q(red_def=self.id) | Q(blue_att=self.id) | Q(blue_def=self.id)) \
            .order_by('-date')


class MemberManager(models.Manager):
    def get_queryset(self):
        queryset = super(MemberManager, self).get_queryset()
        queryset = queryset.annotate(won=F('offence') + F('defence'))
        queryset = queryset.annotate(lost=F('played') - F('won'))
        queryset = queryset.annotate(att_ratio=ExpressionWrapper(
            Case(
                When(won=0, then=0.0),
                default=Round(F('offence') / F('won'), place=2)
            ),
            output_field=models.FloatField()
        ))
        queryset = queryset.annotate(def_ratio=ExpressionWrapper(
            Case(
                When(won=0, then=0.0),
                default=Round(F('defence') / F('won'), place=2)
            ),
            output_field=models.FloatField()
        ))
        queryset = queryset.annotate(win_ratio=ExpressionWrapper(
            Case(
                When(played=0, then=0.0),
                default=Round(F('won') / F('played'), place=2)
            ),
            output_field=models.FloatField()
        ))
        return queryset


class Member(models.Model):
    objects = MemberManager()

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    username = models.CharField(max_length=14, blank=False, null=False)
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

    def __str__(self):
        return self.username

    def get_latest_matches(self):
        latest = Match.objects.all()
        latest = latest.filter(Q(red_att=self.id) | Q(red_def=self.id) | Q(blue_att=self.id) | Q(blue_def=self.id))
        latest = latest.order_by('-date')
        return latest

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
        :return: The amount of points that red team should gain and information whether red team won
        """
        K = int(self.status)
        G = (11+abs(self.red_score - self.blue_score)) / 8
        dr = ((self.red_att.exp + self.red_def.exp) - (self.blue_att.exp + self.blue_def.exp))
        We = 1 / ((10 ** -(dr/400))+1)
        W = 1 if self.red_score > self.blue_score else 0
        return int(K*G*(W-We)), self.red_score > self.blue_score
 
    def save(self, *args, **kwargs):
        self.points, is_red_winner = self.calculate_points()
        self.red_att.after_match_update(self.points, is_red_winner, True)
        self.red_def.after_match_update(self.points, is_red_winner, False)
        self.blue_att.after_match_update(-self.points, not is_red_winner, True)
        self.blue_def.after_match_update(-self.points, not is_red_winner, False)
        super(Match, self).save(*args, **kwargs)


class ExpHistory(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='exp_history')
    date = models.DateField(auto_now_add=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='exp_history', blank=True, null=True)
    exp = models.IntegerField()
