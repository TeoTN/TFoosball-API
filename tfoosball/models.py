from django.db import models
from django.db.models import Q, Func
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class Round(Func):
    function = 'ROUND'
    arity = 1
    template = '%(function)s(%(expressions)s, %(place)d)'


class Team(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]+$', 'Only alphanumeric characters are allowed.')
    domain = models.CharField(max_length=32, validators=[alphanumeric])
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Player(AbstractUser):
    hidden = models.BooleanField(default=False)
    teams = models.ManyToManyField(Team, through='Member')


class Member(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    username = models.CharField(max_length=14, blank=False, null=False)
    exp = models.IntegerField(blank=False, null=False, default=1000)
    offence_won = models.IntegerField(default=0)
    defence_won = models.IntegerField(default=0)
    offence_played = models.IntegerField(default=0)
    defence_played = models.IntegerField(default=0)
    win_streak = models.IntegerField(default=0)
    curr_win_streak = models.IntegerField(default=0)
    lose_streak = models.IntegerField(default=0)
    curr_lose_streak = models.IntegerField(default=0)
    lowest_exp = models.IntegerField(default=1000)
    highest_exp = models.IntegerField(default=1000)
    is_team_admin = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return '{0} ({1})'.format(self.username, self.team.name)

    @property
    def played(self):
        return self.offence_played + self.defence_played

    @property
    def won(self):
        return self.offence_won + self.defence_won

    @property
    def lost(self):
        return self.played - self.won

    @property
    def att_ratio(self):
        return round(self.offence_played / self.offence_won if self.offence_won > 0 else 0, 2)

    @property
    def def_ratio(self):
        return round(self.defence_played / self.defence_won if self.defence_won > 0 else 0, 2)

    @property
    def win_ratio(self):
        return round(self.won / self.played if self.played > 0 else 0, 2)

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

    def update_winner(self, is_offence):
        self.curr_win_streak += 1
        self.curr_lose_streak = 0
        if is_offence:
            self.offence_won += 1
        else:
            self.defence_won += 1

    def update_loser(self):
        self.curr_win_streak = 0
        self.curr_lose_streak += 1

    def update_played_games(self, is_offence):
        if is_offence:
            self.offence_played += 1
        else:
            self.defence_played += 1

    def after_match_update(self, points, winner, is_offence):
        self.exp += points
        self.update_played_games(is_offence)

        if winner == 1:
            self.update_winner(is_offence)
        elif winner == 0:
            self.update_loser()

        self.update_extremes()
        self.save()


class MatchQuerySet(models.QuerySet):
    def by_team(self, team_id):
        return self.filter(
            Q(red_att__team__id=team_id) &
            Q(red_def__team__id=team_id) &
            Q(blue_att__team__id=team_id) &
            Q(blue_def__team__id=team_id)
        )

    def by_username(self, username):
        return self.filter(
            Q(red_att__username=username) |
            Q(red_def__username=username) |
            Q(blue_att__username=username) |
            Q(blue_def__username=username)
        )


class MatchManager(models.Manager):
    def get_queryset(self):
        return MatchQuerySet(self.model, using=self._db)

    def by_team(self, team_id):
        return self.get_queryset().by_team(team_id)

    def by_username(self, username):
        return self.get_queryset().by_username(username)


class Match(models.Model):
    WINNER_CHOICES = (
        (1, 'red'),
        (0, 'blue'),
        (0.5, 'tie')
    )
    objects = MatchManager()

    red_att = models.ForeignKey(Member, related_name='red_att')
    red_def = models.ForeignKey(Member, related_name='red_def')
    blue_att = models.ForeignKey(Member, related_name='blue_att')
    blue_def = models.ForeignKey(Member, related_name='blue_def')
    date = models.DateTimeField(auto_now_add=True, blank=True)
    red_score = models.IntegerField()
    blue_score = models.IntegerField()
    points = models.IntegerField()
    status = models.IntegerField(default=20)

    @property
    def users(self):
        return [self.red_att, self.red_def, self.blue_def, self.blue_att]

    @property
    def attackers(self):
        return [self.red_att, self.blue_att]

    @property
    def defenders(self):
        return [self.red_def, self.blue_def]

    def update_players(self, winner):
        self.red_att.after_match_update(self.points, winner, True)
        self.red_def.after_match_update(self.points, winner, False)
        self.blue_att.after_match_update(-self.points, winner, True)
        self.blue_def.after_match_update(-self.points, winner, False)

    def calculate_points(self):
        """
        :return: The amount of points that red team should gain and information about winner mapped as in WINNER_CHOICES
        """
        assert(self.red_score >= 0 and self.blue_score >= 0)
        K = int(self.status)
        G = (11 + abs(self.red_score - self.blue_score)) / 8
        dr = ((self.red_att.exp + self.red_def.exp) - (self.blue_att.exp + self.blue_def.exp))
        We = 1 / ((10 ** -(dr / 400)) + 1)
        W = 0.5 if self.red_score == self.blue_score else (1 if self.red_score > self.blue_score else 0)
        return int(K * G * (W - We)), W

    def save(self, *args, **kwargs):
        self.points, winner = self.calculate_points()
        self.update_players(winner)
        super(Match, self).save(*args, **kwargs)


class ExpHistory(models.Model):
    player = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='exp_history')
    date = models.DateField(auto_now_add=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='exp_history', blank=True, null=True)
    exp = models.IntegerField()
