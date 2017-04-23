from rest_framework import serializers
from tfoosball.models import Player, Member, Match, Team
from django.db.models import Func, F


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 0)'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'email', 'first_name', 'last_name',)


class MemberSerializer(serializers.ModelSerializer):
    exp_history = serializers.SerializerMethodField()
    att_ratio = serializers.SerializerMethodField()
    def_ratio = serializers.SerializerMethodField()
    win_ratio = serializers.SerializerMethodField()
    email = serializers.CharField(source='player.email', read_only=True)
    first_name = serializers.CharField(source='player.first_name', read_only=True)
    last_name = serializers.CharField(source='player.last_name', read_only=True)

    def get_att_ratio(self, obj):
        return obj.att_ratio

    def get_def_ratio(self, obj):
        return obj.def_ratio

    def get_win_ratio(self, obj):
        return obj.win_ratio

    def get_exp_history(self, obj):
        return obj.exp_history.all() \
            .values('date')\
            .annotate(daily_avg=F('exp'))\
            .annotate(amount=F('matches_played'))\
            .order_by('date')

    class Meta:
        model = Member
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'exp', 'played', 'att_ratio', 'def_ratio',
            'win_ratio', 'win_streak', 'lose_streak', 'curr_lose_streak', 'curr_win_streak', 'lowest_exp',
            'highest_exp', 'exp_history', 'is_accepted',
        )


class MatchSerializer(serializers.ModelSerializer):
    red_att = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    red_def = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    blue_att = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    blue_def = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    points = serializers.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        # Ensure that we use only members within team context, if present
        ctx = kwargs.get('context', None)
        if not ctx:
            super(MatchSerializer, self).__init__(*args, **kwargs)
            return
        team_id = ctx['view'].kwargs.get('parent_lookup_team', None)
        if team_id:
            fields = ['red_att', 'red_def', 'blue_att', 'blue_def']
            for field_name in fields:
                field = self.fields[field_name]
                field.queryset = field.queryset.filter(team_id=team_id)
        super(MatchSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Match
        fields = (
            'id', 'red_att', 'red_def', 'blue_att', 'blue_def', 'date',
            'red_score', 'blue_score', 'points'
        )
