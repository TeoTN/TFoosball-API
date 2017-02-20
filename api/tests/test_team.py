from django.test import TestCase
from django.forms.models import model_to_dict
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import TeamViewSet
from tfoosball.models import Player, Team
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
