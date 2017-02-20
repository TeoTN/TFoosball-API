from django.test import TestCase
from django.db.models import F
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import TeamViewSet
from api.serializers import TeamSerializer
from tfoosball.models import Player, Team, Member
import json

factory = APIRequestFactory()


class TeamJoinedTestCase(TestCase):
    fixtures = ['players.json', 'teams.json', 'members.json']

    def setUp(self):
        self.admin_user = Player.objects.get(username='admin')
        self.dev_team = Team.objects.get(domain='dev')
        self.fields = ('id', 'name')

    def test_get_joined_teams(self):
        teams = Team.objects.filter(member__player__id=self.admin_user.id)
        teams = teams.annotate(username=F('member__username'), member_id=F('member__id'))
        expected_data = [
            {'id': team.id, 'name': team.name, 'username': team.username, 'member_id': team.member_id}
            for team in teams
        ]
        request = factory.get('/api/teams/joined/')
        force_authenticate(request, user=self.admin_user)
        view = TeamViewSet.as_view({'get': 'joined'})
        response = view(request)
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(response_data, expected_data, 'expected correct number of teams')