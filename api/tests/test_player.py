from django.test import TestCase
from django.forms.models import model_to_dict
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import PlayerViewSet
from tfoosball.models import Player
import json

factory = APIRequestFactory()


class PlayerEndpointTestCase(TestCase):
    fixtures = ['players.json']

    def setUp(self):
        self.admin_user = Player.objects.get(username='admin')
        self.fields = ('id', 'first_name', 'last_name', 'email')

    def test_get_list(self):
        request = factory.get('/api/players/')
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(len(response_data), Player.objects.count(), 'expected correct number of players')

    def test_get_item(self):
        request = factory.get('/api/players/1/')
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk='1')
        response.render()
        expected_data = model_to_dict(self.admin_user, fields=self.fields)
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertDictEqual(response.data, expected_data, 'expected user admin data')

    def test_autocompletion(self):
        players = Player.objects.filter(email__istartswith='p')
        request = factory.get('/api/players/?email_prefix=p')
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'get': 'list'})
        response = view(request)
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(len(response_data), players.count(), 'expected correct number of players')
