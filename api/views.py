from smtplib import SMTPException
from uuid import uuid4
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin, DetailSerializerMixin

from api.emailing import send_invitation
from tfoosball.models import Member, Match, Player, Team, WhatsNew
from .serializers import (
    MatchSerializer,
    MemberSerializer,
    TeamSerializer,
    PlayerSerializer,
    WhatsNewSerializer,
    TeamDetailSerializer,
    MemberDetailSerializer
)
from .permissions import MemberPermissions, AccessOwnTeamOnly, IsMatchOwner


def displayable(message):
    return {
        'shouldDisplay': True,
        'message': message,
    }


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class TeamViewSet(NestedViewSetMixin, DetailSerializerMixin, ModelViewSet):
    serializer_class = TeamSerializer
    serializer_detail_class = TeamDetailSerializer
    allowed_methods = [u'GET', u'POST', u'OPTIONS']
    filter_fields = ('name',)

    def get_queryset(self):
        queryset = Team.objects.all()
        prefix = self.request.query_params.get('name_prefix', None)
        if prefix:
            queryset = queryset.filter(name__istartswith=prefix)[:5]
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        if 'username' in request.data:
            member = Member.objects.create(
                team=instance,
                player=request.user,
                username=request.data['username'],
                is_team_admin=True,
                is_accepted=True
            )
            response_data.update({'member_id': member.id})
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def joined(self, request):
        """
        :param request:
        :return: A list of teams that request user has joined
        """
        teams = Team.objects.filter(member__player__id=request.user.id, member__is_accepted=True)
        teams_pending = Team.objects.filter(member__player__id=request.user.id, member__is_accepted=False).count()
        teams = teams.annotate(username=F('member__username'), member_id=F('member__id'))
        teams_data = [
            {'id': team.id, 'name': team.name, 'username': team.username, 'member_id': team.member_id}
            for team in teams
        ]
        data = {
            'teams': teams_data,
            'pending': teams_pending,
        }
        return Response(data, status.HTTP_200_OK)

    @list_route(methods=['post'])
    def join(self, request):
        """
        This endpoint allows request user to join given team
        :param request: HttpRequest object with user field
        :return: Response
        """
        username = request.data.get('username', None)
        teamname = request.data.get('team', None)
        if not username:
            return Response('Missing username', status=status.HTTP_400_BAD_REQUEST)
        if not teamname:
            return Response('Missing team name', status=status.HTTP_400_BAD_REQUEST)
        try:
            team = Team.objects.get(name=teamname)
        except Team.DoesNotExist:
            return Response('Team does not exist', status=status.HTTP_404_NOT_FOUND)
        member, created = Member.objects.get_or_create(
            team=team,
            player=request.user,
            username=username[:14],
            is_accepted=False,
        )
        if created:
            return Response(
                'Please wait until a club member confirms your request.',
                status=status.HTTP_201_CREATED
            )
        return Response(
            data='You have already requested membership in team {0}'.format(team.name),
            status=status.HTTP_409_CONFLICT
        )

    @list_route(methods=['post'])
    def accept(self, request):
        activation_code = request.data.get('activation_code', None)
        if not activation_code:
            return Response(displayable('Unable to activate user'), status=status.HTTP_400_BAD_REQUEST)
        print(activation_code)
        email, team_name, token, token2 = activation_code.split(':')
        if request.user.email != email:
            return Response(displayable('Unable to activate user'), status=status.HTTP_400_BAD_REQUEST)
        try:
            member = Member.objects.get(activation_code=activation_code)
            member.activate()
        except (ValidationError, BadSignature):
            return Response(displayable('Unable to activate user'), status=status.HTTP_400_BAD_REQUEST)
        except SignatureExpired:
            return Response(
                displayable('Activation code has expired after 48 hours'),
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(displayable('User activated'), status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'], permission_classes=[AccessOwnTeamOnly])
    def invite(self, request, pk=None):
        username = request.data.get('username', f'user-{str(uuid4())[:8]}')  # TODO Better default username
        email = request.data.get('email', None)
        team = Team.objects.get(pk=pk)
        if not email:
            return Response(displayable('You haven\'t provided an email'), status=status.HTTP_400_BAD_REQUEST)
        is_member = team.member_set.filter(player__email=email).exists()
        if is_member:
            return Response(
                displayable('User of email {0} is already a member of {1}'.format(email, team.name)),
                status=status.HTTP_409_CONFLICT
            )
        member, placeholder = Member.create_member(
            username, email, pk,
            is_accepted=True,
            hidden=True,
            invitation_date=timezone.now()
        )
        activation_code = member.generate_activation_code()
        try:
            send_invitation(email, activation_code)
        except SMTPException:
            return Response(
                'Unknown error while sending an invitation, please try again.',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            # TODO Revert member
        else:
            return Response(
                displayable('Invitation was sent to {0}'.format(email)),
                status=status.HTTP_201_CREATED
            )


class MemberViewSet(NestedViewSetMixin, ModelViewSet):
    filter_fields = ('is_accepted', 'username', 'hidden')
    permission_classes = (MemberPermissions,)

    def get_serializer_class(self, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        if self.action == 'retrieve' or username:
            return MemberDetailSerializer
        return MemberSerializer

    def get_queryset(self):
        team = self.kwargs.get('parent_lookup_team', None)
        is_accepted = self.request.query_params.get('is_accepted', True)
        pk = self.kwargs.get('pk', None)
        username = self.request.query_params.get('username', None)
        if team and username:
            return Member.objects.filter(team__id=team, username=username)
        if pk or username:
            return Member.objects.all()
        if team:
            return Member.objects.filter(
                hidden=False,
                is_accepted=is_accepted,
                team__pk=team
            )
        return Member.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        team = instance.team
        is_last = team.member_set.count() == 1
        self.perform_destroy(instance)
        if is_last:
            team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MatchViewSet(ModelViewSet):
    serializer_class = MatchSerializer
    allowed_methods = [u'GET', u'POST', u'PUT', u'PATCH', u'DELETE', u'OPTIONS']
    pagination_class = StandardPagination
    permission_classes = [IsMatchOwner]

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
        data = {k + '_id': v for k, v in request.query_params.items()}
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
            queryset = queryset.filter(email__istartswith=prefix)[:5]
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


class WhatsNewViewSet(ModelViewSet):
    serializer_class = WhatsNewSerializer
    allowed_methods = [u'GET', u'OPTIONS']
    queryset = WhatsNew.objects.all()


class EventsViewSet(NestedViewSetMixin, ViewSet):
    def get_club_events(self, team_id):
        date_from = timezone.now() - timezone.timedelta(days=1)
        matches = Match.objects.by_team(team_id=team_id).filter(date__gte=date_from)
        members = Member.objects.filter(team__id=team_id)
        events = matches.get_events() + members.get_events()
        return sorted(events, key=lambda ev: ev['date'], reverse=True)

    def list(self, request, *args, **kwargs):
        team_id = kwargs.get('parent_lookup_team', None)
        if not team_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_club_events(team_id))
