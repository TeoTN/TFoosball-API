from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from tfoosball.models import Member, Match, Player, Team
from .serializers import MatchSerializer, MemberSerializer, TeamSerializer, PlayerSerializer
from .permissions import MemberPermissions


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class TeamViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = TeamSerializer
    allowed_methods = [u'GET', u'POST', u'OPTIONS']

    def get_queryset(self):
        return Team.objects.all()

    @list_route(methods=['get'])
    def joined(self, request):
        """
        :param request:
        :return: A list of teams that request user has joined
        """
        teams = Team.objects.filter(member__player__id=request.user.id)
        teams = teams.annotate(username=F('member__username'), member_id=F('member__id'))
        data = [
            {'id': team.id, 'name': team.name, 'username': team.username, 'member_id': team.member_id}
            for team in teams
        ]
        return Response(data, status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def join(self, request, pk=None):
        """
        This endpoint allows request user to join given team
        :param request: HttpRequest object with user field
        :return: Response
        """
        username = request.data.get('username', None)
        if not username:
            return Response('Missing parameter username', status=status.HTTP_400_BAD_REQUEST)
        try:
            team = self.get_object()
        except:
            return Response('Team does not exist', status=status.HTTP_404_NOT_FOUND)
        member, created = Member.objects.get_or_create(
            team=team,
            player=request.user,
            username=username[:14],
            is_accepted=False,
        )
        if created:
            return Response('Please wait for somebody to accept your join request.', status=status.HTTP_201_CREATED)
        return Response(
            data='You have already requested membership in team {0}'.format(team.name),
            status=status.HTTP_409_CONFLICT
        )


class MemberViewSet(NestedViewSetMixin, ModelViewSet):
    serializer_class = MemberSerializer
    filter_fields = ('is_accepted', 'username')
    permission_classes = (MemberPermissions,)

    def get_queryset(self):
        team = self.kwargs.get('parent_lookup_team', None)
        if team:
            return Member.objects.filter(
                player__hidden=False,
                is_accepted=True,
                team__pk=team
            )
        return Member.objects.all()


class MatchViewSet(ModelViewSet):
    serializer_class = MatchSerializer
    allowed_methods = [u'GET', u'POST', u'PUT', u'PATCH', u'DELETE', u'OPTIONS']
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Match.objects.all()
        team_id = self.kwargs.get('parent_lookup_team', None)
        username = self.request.query_params.get('username', None)
        if team_id:
            queryset = queryset.by_team(team_id)
        if username:
            queryset = queryset.by_username(username)
        queryset = queryset.order_by('-date')
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(MatchViewSet, self).list(request, args, kwargs)
        response.data['page'] = request.GET.get('page', 1)
        response.data['page_size'] = request.GET.get('page_size', StandardPagination.page_size)
        return response

    @list_route(methods=['get'])
    def points(self, request, *args, **kwargs):
        data = {k+'_id': v for k, v in request.query_params.items()}
        match = Match(**data, red_score=0, blue_score=10)
        try:
            result1 = abs(match.calculate_points()[0])
        except (Match.red_att.RelatedObjectDoesNotExist,
                Match.red_def.RelatedObjectDoesNotExist,
                Match.blue_att.RelatedObjectDoesNotExist,
                Match.blue_def.RelatedObjectDoesNotExist):
            return Response({'detail': 'Players have not been provided'}, status=406)
        match = Match(**data, red_score=10, blue_score=0)
        result2 = abs(match.calculate_points()[0])
        return Response({'blue': result1, 'red': result2})


class PlayerViewSet(ModelViewSet):
    serializer_class = PlayerSerializer
    allowed_methods = [u'GET', u'OPTIONS']

    def get_queryset(self):
        queryset = Player.objects.all()
        prefix = self.request.query_params.get('email_prefix', None)
        if prefix:
            queryset = queryset.filter(email__istartswith=prefix)
        return queryset

    @detail_route(methods=['post'])
    def invite(self, request, *args, **kwargs):
        team__id = request.data.get('team', None)
        username = request.data.get('username', None)
        player__id = kwargs.get('pk', None)
        if team__id is None or player__id is None or username is None:
            return Response({'detail': 'Missing team, username or player id'}, status=status.HTTP_400_BAD_REQUEST)
        team = get_object_or_404(Team, pk=team__id)
        player = get_object_or_404(Player, pk=player__id)

        try:
            member, created = Member.objects.get(team=team, player=player), False
        except Member.DoesNotExist:
            member, created = Member.objects.create(team=team, player=player, username=username[:14]), True
        if created:
            return Response(model_to_dict(member), status=status.HTTP_201_CREATED)
        err_msg = 'Player {0} already is a member of {1} team'.format(member.username, team.name)
        return Response({'detail': err_msg}, status=status.HTTP_400_BAD_REQUEST)

