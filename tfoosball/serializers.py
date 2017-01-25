from rest_framework import serializers
from .models import Player, Match
from django.db.models import Avg, Func


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 0)'


class UserSerializer(serializers.ModelSerializer):
    exp_history = serializers.SerializerMethodField()

    def get_exp_history(self, obj):
        return obj.exp_history.all().values('date').annotate(daily_avg=Round(Avg('exp'))).order_by('date')

    class Meta:
        model = Player
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'exp',
            'played',
            'att_ratio',
            'def_ratio',
            'win_ratio',
            'win_streak',
            'lose_streak',
            'curr_lose_streak',
            'curr_win_streak',
            'lowest_exp',
            'highest_exp',
            'exp_history',
        )


class MatchSerializer(serializers.ModelSerializer):
    red_att = serializers.SlugRelatedField(slug_field='username', queryset=Player.objects.all())
    red_def = serializers.SlugRelatedField(slug_field='username', queryset=Player.objects.all())
    blue_att = serializers.SlugRelatedField(slug_field='username', queryset=Player.objects.all())
    blue_def = serializers.SlugRelatedField(slug_field='username', queryset=Player.objects.all())
    points = serializers.IntegerField(required=False)

    class Meta:
        model = Match
        fields = (
            'id', 'red_att', 'red_def', 'blue_att', 'blue_def', 'date',
            'red_score', 'blue_score', 'points'
        )
