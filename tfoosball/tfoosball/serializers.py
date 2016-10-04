from rest_framework import serializers
from .models import Player, Match


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'exp',
            'att_ratio',
            'def_ratio',
            'win_streak',
            'lose_streak',
            'lowest_exp',
            'highest_exp'
        )


class MatchSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(required=False)

    class Meta:
        model = Match
        fields = ('red_att', 'red_def', 'blue_att', 'blue_def', 'date', 'red_score', 'blue_score', 'points')
