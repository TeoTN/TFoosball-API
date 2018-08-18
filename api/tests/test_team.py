from django.test import TestCase
from django.forms.models import model_to_dict
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import TeamViewSet
from tfoosball.models import Player, Team, Member
import json

factory = APIRequestFactory()


class TeamEndpointTestCase(TestCase):
    fixtures = ['admin.json', 'teams.json']

    def setUp(self):
        self.admin_user = Player.objects.get(username='admin')
        self.dev_team = Team.objects.get(domain='dev')
        self.fields = ('id', 'name')

    def test_get_list(self):
        request = factory.get('/api/teams/')
        force_authenticate(request, user=self.admin_user)
        view = TeamViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(len(response_data), Team.objects.count(), 'expected correct number of teams')

    def test_get_item(self):
        request = factory.get('/api/teams/{0}/'.format(self.dev_team.id))
        force_authenticate(request, user=self.admin_user)
        view = TeamViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=str(self.dev_team.id))
        response.render()
        expected_data = model_to_dict(self.dev_team, fields=self.fields)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertDictEqual(response.data, expected_data, 'expected dev team data')

    def test_post_list(self):
        request = factory.post('/api/teams/', data={'name': 'Frogz', 'username': 'Ezyme'})
        force_authenticate(request, user=self.admin_user)
        view = TeamViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        team = Team.objects.filter(name='Frogz')
        self.assertEqual(team.count(), 1, 'Expected team to be created')
        member = Member.objects.filter(player=self.admin_user, team=team[0], username='Ezyme')
        self.assertEqual(member.count(), 1, 'Expected member to be created')
        expected_data = {'id': team[0].id, 'name': team[0].name, 'member_id': member[0].id}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'expected HTTP 201 - Created')
        self.assertTrue(
            expected_data.items() <= response.data.items(),
            'Expected appropriate data scheme to be in response'
        )
