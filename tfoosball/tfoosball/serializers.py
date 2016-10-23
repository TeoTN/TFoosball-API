from rest_framework import serializers
from .models import Player, Match, ExpHistory
from django.db.models import Avg


class UserSerializer(serializers.ModelSerializer):
    exp_history = serializers.SerializerMethodField()

    def get_exp_history(self, obj):
        return obj.exp_history.all().values('date').annotate(daily_avg=Avg('exp'))

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
    points = serializers.IntegerField(required=False)

    class Meta:
        model = Match
        fields = ('red_att', 'red_def', 'blue_att', 'blue_def', 'date', 'red_score', 'blue_score', 'points')
