from django.test import TestCase
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import MatchViewSet
from api.serializers import MatchSerializer
from tfoosball.models import Player, Team, Match
import json

factory = APIRequestFactory()


class TeamMatchesEndpointTestCase(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json', 'matches.json']

    def setUp(self):
        self.admin_user = Player.objects.get(username='admin')
        self.dev_team = Team.objects.get(domain='dev')
        self.fields = (
            'id',
        )

    def test_get_list(self):
        matches = Match.objects.by_team(self.dev_team.id)
        request = factory.get('/api/teams/{0}/matches/'.format(self.dev_team.id))
        force_authenticate(request, user=self.admin_user)
        view = MatchViewSet.as_view({'get': 'list'})
        response = view(request, parent_lookup_team=str(self.dev_team.id))
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(response_data['count'], matches.count(), 'expected correct number of dev team matches')

    def test_get_item(self):
        match = Match.objects.get(pk=9)
        request = factory.get('/api/teams/{0}/matches/9/'.format(self.dev_team.id))
        force_authenticate(request, user=self.admin_user)
        view = MatchViewSet.as_view({'get': 'retrieve'})
        response = view(request, parent_lookup_team=str(self.dev_team.id), pk='9')
        response.render()
        expected_data = MatchSerializer(match).data
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        for rk, ek in zip(response.data.keys(), expected_data.keys()):
            self.assertEqual(str(response.data[rk]), str(expected_data[ek]), 'expected correct match data')

    def test_filter_by_username(self):
        matches = Match.objects.by_team(self.dev_team.id).by_username('kscott8')
        request = factory.get('/api/teams/{0}/matches/?username=kscott8'.format(self.dev_team.id))
        force_authenticate(request, user=self.admin_user)
        view = MatchViewSet.as_view({'get': 'list'})
        response = view(request, parent_lookup_team=str(self.dev_team.id))
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(response_data['count'], matches.count(), 'expected matches filtered by username')

    def test_count_points_invalid(self):
        request = factory.get('/api/teams/{0}/matches/points/'.format(self.dev_team.id))
        force_authenticate(request, user=self.admin_user)
        view = MatchViewSet.as_view({'get': 'points'})
        response = view(request, parent_lookup_team=str(self.dev_team.id))
        response.render()
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE, 'expected HTTP 406 - Not acceptable')

    def test_count_points(self):
        request = factory.get(
            '/api/teams/{0}/matches/points/?red_att=8&red_def=8&blue_att=8&blue_def=8'.format(self.dev_team.id))
        force_authenticate(request, user=self.admin_user)
        view = MatchViewSet.as_view({'get': 'points'})
        response = view(request, parent_lookup_team=str(self.dev_team.id))
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(response_data, {"red": 26, "blue": 26}, 'expected correct match points')
