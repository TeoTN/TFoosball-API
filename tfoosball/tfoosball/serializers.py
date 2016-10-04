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
    class Meta:
        model = Match
        fields = ('__all__',)
