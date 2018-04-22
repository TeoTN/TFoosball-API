from rest_framework import serializers
from rest_framework.reverse import reverse

from tfoosball.models import Player, Member, Match, Team, WhatsNew
from django.db.models import Func, F


class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 0)'


class TeamSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ('id', 'name', 'links')

    def get_links(self, obj):
        return {
            'instance': reverse('api:team-detail', args=[obj.id], request=self.context['request']),
            'members': reverse('api:team-member-list', args=[obj.id], request=self.context['request']),
            'matches': reverse('api:team-matches-list', args=[obj.id], request=self.context['request'])
        }


class TeamDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'email', 'first_name', 'last_name', 'whats_new_version', 'default_team')


class MemberSerializer(serializers.ModelSerializer):
    att_ratio = serializers.SerializerMethodField()
    def_ratio = serializers.SerializerMethodField()
    win_ratio = serializers.SerializerMethodField()
    # TODO Consider nested serializer
    email = serializers.CharField(source='player.email', read_only=True)
    first_name = serializers.CharField(source='player.first_name', default='')
    last_name = serializers.CharField(source='player.last_name', default='')
    whats_new_version = serializers.IntegerField(source='player.whats_new_version', read_only=True)
    default_team = serializers.IntegerField(source='player.default_team.pk', default=-1)
    user_id = serializers.IntegerField(source='player.pk', read_only=True)

    class Meta:
        model = Member
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'exp', 'played', 'att_ratio', 'def_ratio',
            'win_ratio', 'win_streak', 'lose_streak', 'curr_lose_streak', 'curr_win_streak', 'lowest_exp',
            'default_team', 'highest_exp', 'is_accepted', 'hidden', 'whats_new_version', 'user_id',
            'is_team_admin',
        )

    def create(self, validated_data):
        validated_data.pop('first_name')
        validated_data.pop('last_name')
        validated_data.pop('default_team')
        return super(MemberSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        player_data = validated_data.pop('player', None)
        updated = super(MemberSerializer, self).update(instance, validated_data)
        if player_data:
            Player.objects.filter(id=updated.player.id).update(**player_data)
        return updated

    def get_att_ratio(self, obj):
        return obj.att_ratio

    def get_def_ratio(self, obj):
        return obj.def_ratio

    def get_win_ratio(self, obj):
        return obj.win_ratio


class MemberDetailSerializer(MemberSerializer):
    exp_history = serializers.SerializerMethodField()

    class Meta:
        fields = MemberSerializer.Meta.fields + ('exp_history',)
        model = Member

    def get_exp_history(self, obj):
        return obj.exp_history.all() \
            .values('date') \
            .annotate(daily_avg=F('exp')) \
            .annotate(amount=F('matches_played')) \
            .order_by('date')


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

    def validate(self, data):
        rs = data.get('red_score', None)
        bs = data.get('blue_score', None)
        if rs == 0 and bs == 0:
            raise serializers.ValidationError('Cannot add match with score 0-0. Was it a typo?')
        return data


class WhatsNewSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'content', 'links')
        model = WhatsNew

    def get_links(self, obj):
        return {
            'instance': reverse('api:whatsnew-detail', args=[obj.id], request=self.context['request']),
        }
