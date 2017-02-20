from django.test import TestCase
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import PlayerViewSet
from tfoosball.models import Player, Team

factory = APIRequestFactory()


class PlayerInvitationTestCase(TestCase):
    fixtures = ['players.json', 'teams.json']

    def setUp(self):
        self.admin_user = Player.objects.get(username='admin')
        self.team = Team.objects.get(domain='unk')

    def test_invite(self):
        request_data = {
            'team': self.team.id,
            'username': 'random',
        }
        request = factory.post('/api/players/1/invite/', request_data)
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'post': 'invite'})
        response = view(request, pk='1')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'expected HTTP 201 - Created')

    def test_invite_missing_team(self):
        request_data = {
            'username': 'random',
        }
        request = factory.post('/api/players/1/invite/', request_data)
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'post': 'invite'})
        response = view(request, pk='1')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'expected HTTP 400 - Bad request')

    def test_invite_missing_username(self):
        request_data = {
            'team': self.team.id,
        }
        request = factory.post('/api/players/1/invite/', request_data)
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'post': 'invite'})
        response = view(request, pk='1')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'expected HTTP 400 - Bad request')

    def test_invite_team_not_found(self):
        request_data = {
            'team': '1234567',
            'username': 'random',
        }
        request = factory.post('/api/players/1/invite/', request_data)
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'post': 'invite'})
        response = view(request, pk='1')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'expected HTTP 404 - Not found')

    def test_invite_player_not_found(self):
        request_data = {
            'team': '2',
            'username': 'random',
        }
        request = factory.post('/api/players/10000/invite/', request_data)
        force_authenticate(request, user=self.admin_user)
        view = PlayerViewSet.as_view({'post': 'invite'})
        response = view(request, pk='10000')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'expected HTTP 404 - Not found')
