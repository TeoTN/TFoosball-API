from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.signing import TimestampSigner
from django.db import models
from django.db.models import Q, Func
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


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
    teams = models.ManyToManyField(Team, through='Member')
    whats_new_version = models.IntegerField(default=0)  # Latest seen what's new modal version
    default_team = models.ForeignKey(Team, blank=True, null=True, related_name='default_team', on_delete=models.CASCADE)


class MemberQuerySet(models.QuerySet):
    def get_events(self):
        events = []
        for member in self.all():
            events.append(member.get_invitation_event())
            events.append(member.get_joined_event())
        return list(filter(None, events))


class MemberManager(models.Manager):
    def get_queryset(self):
        return MemberQuerySet(self.model, using=self._db)

    def get_events(self):
        return self.get_queryset().get_events()


class Member(models.Model):
    WINNER = 1
    LOSER = 0
    username_len = 32
    objects = MemberManager()

    class Meta:
        unique_together = (('team', 'username'),)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True, null=True)
    username = models.CharField(max_length=username_len, blank=False, null=False)
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
    hidden = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=384, default='', blank=True)
    invitation_date = models.DateTimeField(blank=True, null=True)
    joined_date = models.DateTimeField(blank=True, null=True)

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
        return round(self.offence_won / self.offence_played if self.offence_played > 0 else 0, 2)

    @property
    def def_ratio(self):
        return round(self.defence_won / self.defence_played if self.defence_played > 0 else 0, 2)

    @property
    def win_ratio(self):
        return round(self.won / self.played if self.played > 0 else 0, 2)

    def get_matches(self):
        return Match.objects.filter(Q(red_att=self.id) | Q(red_def=self.id) | Q(blue_att=self.id) | Q(blue_def=self.id))

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

    def after_match_update(self, points, result, is_offence, save=True):
        self.exp += points
        self.update_played_games(is_offence)

        if result == self.WINNER:
            self.update_winner(is_offence)
        elif result == self.LOSER:
            self.update_loser()

        self.update_extremes()
        if save:
            self.save()

    @staticmethod
    def create_member(username, email, team_id, is_accepted=False, **kwargs):
        member_data = {'team_id': team_id, 'username': username, 'is_accepted': is_accepted}
        member_data.update(kwargs)
        try:
            player = Player.objects.get(email=email)
            member = Member.objects.create(**member_data, player=player)
            is_placeholder = False
        except Player.DoesNotExist:
            member = Member.objects.create(**member_data)
            try:
                PlayerPlaceholder.objects.get(member=member, email=email)
            except PlayerPlaceholder.DoesNotExist:
                PlayerPlaceholder.objects.create(member=member, email=email)
            is_placeholder = True
        return member, is_placeholder

    def generate_activation_code(self):
        email = self.player.email if self.player else self.placeholder.first().email
        value = '{0}:{1}'.format(email, self.team.name)
        signer = TimestampSigner()
        self.activation_code = signer.sign(value)
        self.save()
        return self.activation_code

    def activate(self):
        """
        Function will activate member with given code if it's valid and not expired.
        :raises signing.BadSignature: Activation code was tampered
        :raises signing.SignatureExpired: Activation code has expired after 48h
        :raises ValidationError: The member was already activated
        :return: None
        """
        if self.activation_code == '':
            raise ValidationError('The member is already activated')
        signer = TimestampSigner()
        signer.unsign(self.activation_code, max_age=timedelta(days=2))
        self.hidden = False
        self.activation_code = ''
        self.joined_date = timezone.now()
        self.save()

    def get_invitation_event(self):
        return {
            'date': self.invitation_date,
            'event': f'Invitation to ***{self.get_email()}*** has been sent',
            'type': 'invitation'
        } if self.invitation_date else None

    def get_joined_event(self):
        return {
            'date': self.joined_date,
            'event': f'Member ***[{self.username}]({self.get_profile_link()})*** has joined',
            'type': 'joined'
        } if self.joined_date else None

    def get_email(self):
        return self.player.email if self.player else self.placeholder.all().first().email

    def get_profile_link(self):
        return f'/profile/{self.username}/stats'


class PlayerPlaceholder(models.Model):
    member = models.ForeignKey(Member, related_name='placeholder', on_delete=models.CASCADE)
    email = models.EmailField()

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        is_not_unique = PlayerPlaceholder.objects.filter(email=self.email, member__team=self.member.team).exists()
        if is_not_unique:
            raise ValidationError('Player is already expected to be assigned to the team')

    def save(self, *args, **kwargs):
        self.validate_unique()
        return super().save(*args, **kwargs)

    def __str__(self):
        return '{0} ({1})'.format(self.email, self.member.team.name)


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

    def get_events(self):
        return [match.get_event() for match in self.all()]


class MatchManager(models.Manager):
    def get_queryset(self):
        return MatchQuerySet(self.model, using=self._db)

    def by_team(self, team_id):
        return self.get_queryset().by_team(team_id)

    def by_username(self, username):
        return self.get_queryset().by_username(username)

    def get_events(self):
        return self.get_queryset().get_events()


class Match(models.Model):
    RED = 1
    BLUE = 0
    TIE = 0.5

    WINNER_CHOICES = (
        (RED, 'red'),
        (BLUE, 'blue'),
        (TIE, 'tie')
    )
    objects = MatchManager()

    class Meta:
        verbose_name_plural = "matches"

    red_att = models.ForeignKey(Member, related_name='red_att', on_delete=models.CASCADE)
    red_def = models.ForeignKey(Member, related_name='red_def', on_delete=models.CASCADE)
    blue_att = models.ForeignKey(Member, related_name='blue_att', on_delete=models.CASCADE)
    blue_def = models.ForeignKey(Member, related_name='blue_def', on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True)
    red_score = models.IntegerField()
    blue_score = models.IntegerField()
    points = models.IntegerField()
    status = models.IntegerField(default=20)

    @property
    def users(self):
        return [self.red_att, self.red_def, self.blue_def, self.blue_att]

    @staticmethod
    def create_exp_history(match):
        for player in match.users:
            try:
                eh = ExpHistory.objects.get(player=player, date=match.date)
            except ExpHistory.DoesNotExist:
                eh = ExpHistory(player=player, date=match.date, matches_played=0)
            eh.exp = player.exp
            eh.match = match
            eh.matches_played += 1
            eh.save()

    def get_team_result(self, winner):
        if winner == Match.RED:
            return Member.WINNER, Member.LOSER
        if winner == Match.BLUE:
            return Member.LOSER, Member.WINNER
        return Match.TIE, Match.TIE

    def update_players(self, winner):
        red_result, blue_result = self.get_team_result(winner)
        self.red_att.after_match_update(self.points, red_result, True)
        self.red_def.after_match_update(self.points, red_result, False)
        self.blue_att.after_match_update(-self.points, blue_result, True)
        self.blue_def.after_match_update(-self.points, blue_result, False)

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
        if not self.date:
            self.date = timezone.now()
        super(Match, self).save(*args, **kwargs)

    def __str__(self):
        return f'Match {self.red_def.username} {self.red_att.username} - ' \
               f'{self.blue_att.username} {self.blue_def.username} ' \
               f'[{self.red_score} - {self.blue_score}]'

    def get_event(self):
        rdname = self.red_def.username
        rdlink = self.red_def.get_profile_link()
        raname = self.red_att.username
        ralink = self.red_att.get_profile_link()
        bdname = self.blue_def.username
        bdlink = self.blue_def.get_profile_link()
        baname = self.blue_att.username
        balink = self.blue_att.get_profile_link()
        return {
            'date': self.date,
            'event': f'Match was played: ***[{rdname}]({rdlink})***, ***[{raname}]({ralink})*** vs. '
                     f'***[{baname}]({balink})***, ***[{bdname}]({bdlink})***.' + '\n\n'
                     f'###### Score: **{self.red_score}**&nbsp;-&nbsp;**{self.blue_score}**',
            'type': 'match'
        }


class ExpHistory(models.Model):
    class Meta:
        unique_together = (('player', 'date'),)

    player = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='exp_history')
    date = models.DateField(blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='exp_history', blank=True, null=True)
    exp = models.IntegerField()
    matches_played = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)


class WhatsNew(models.Model):
    content = models.TextField(max_length=1536)

    def __str__(self):
        return f'What\'s new v{self.id}'
