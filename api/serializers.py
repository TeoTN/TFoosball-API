from rest_framework import serializers
from tfoosball.models import Player, Member, Match, Team
from django.db.models import Avg, Func, Count


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 0)'


class TeamSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        instance = super(TeamSerializer, self).create(validated_data)
        request = self.context['request']
        if 'username' in request.data:
            Member.objects.create(
                team=instance,
                player=request.user,
                username=request.data['username'],
                is_team_admin=True,
                is_accepted=True
            )
        return instance

    class Meta:
        model = Team
        fields = ('id', 'name')


class PlayerSerializer(serializers.ModelSerializer):
    # teams = serializers.SerializerMethodField()
    #
    # def get_teams(self, obj):
    #     return {
    #         m[2]: {'member_id': m[0], 'username': m[1]}
    #         for m in obj.member_set.values_list('id', 'username', 'team__id')
    #     }

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
            .annotate(daily_avg=Round(Avg('exp')))\
            .annotate(amount=Count('date'))\
            .order_by('date')

    class Meta:
        model = Member
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'exp', 'played', 'att_ratio', 'def_ratio',
            'win_ratio', 'win_streak', 'lose_streak', 'curr_lose_streak', 'curr_win_streak', 'lowest_exp',
            'highest_exp', 'exp_history',
        )


class MatchSerializer(serializers.ModelSerializer):
    red_att = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    red_def = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    blue_att = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    blue_def = serializers.SlugRelatedField(slug_field='username', queryset=Member.objects.all())
    points = serializers.IntegerField(required=False)

    class Meta:
        model = Match
        fields = (
            'id', 'red_att', 'red_def', 'blue_att', 'blue_def', 'date',
            'red_score', 'blue_score', 'points'
        )
