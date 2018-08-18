import unittest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory
from api.views import TeamViewSet
from tfoosball.models import Team, Player, Member, PlayerPlaceholder

factory = APIRequestFactory()


class TeamInviteTestCase(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json']

    def setUp(self):
        self.dev_team = Team.objects.get(name='Developer Team')
        self.member_player = Player.objects.get(username='pflores6')
        self.non_member_player = Player.objects.get(username='phawkins1')
        self.url = '/api/teams/{0}/invite/'.format(self.dev_team.pk)

    @unittest.skip("Skipping test HTTP403 for invite endpoint")
    def test_request_by_non_member(self):
        # TODO Enable the test - migrate to APIClient from APIRequestFactory
        # permission_classes are ignored for @detail_route when using APIRequestFactory
        request = factory.post(self.url)
        force_authenticate(request, user=self.non_member_player)
        view = TeamViewSet.as_view({'post': 'invite'})
        response = view(request, pk=self.dev_team.pk)
        response.render()
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN,
            'expected HTTP 403 when non member sends invitation'
        )

    def test_request_with_missing_email(self):
        request = factory.post(self.url)
        force_authenticate(request, user=self.member_player)
        view = TeamViewSet.as_view({'post': 'invite'})
        response = view(request, pk=self.dev_team.pk)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'expected HTTP 400 on no email')

    def test_invite_already_existing_member(self):
        email = 'lfields7@globo.com'
        request = factory.post(self.url, data={'email': email, 'username': 'LFJ'})
        force_authenticate(request, user=self.member_player)
        view = TeamViewSet.as_view({'post': 'invite'})
        response = view(request, pk=self.dev_team.pk)
        response.render()
        self.assertEqual(
            response.status_code, status.HTTP_409_CONFLICT,
            'expected HTTP 409 when inviting existing member'
        )

    def test_invite_existing_player(self):
        email = self.non_member_player.email
        username = 'PHS'
        request = factory.post(self.url, data={'email': email, 'username': username})
        force_authenticate(request, user=self.member_player)
        view = TeamViewSet.as_view({'post': 'invite'})
        response = view(request, pk=self.dev_team.pk)
        response.render()
        member = Member.objects.filter(team=self.dev_team, username=username)
        self.assertEqual(member.count(), 1, 'Member should have been created')
        self.assertEqual(member[0].player.id, self.non_member_player.id, 'Member should have player assigned')
        self.assertNotEqual(member[0].activation_code, '', 'Activation code should be set')
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            'expected HTTP 201 - Created'
        )

    def test_invite_not_existing_player(self):
        email = 'notexisting@gmail.com'
        username = 'NEX'
        request = factory.post(self.url, data={'email': email, 'username': username})
        force_authenticate(request, user=self.member_player)
        view = TeamViewSet.as_view({'post': 'invite'})
        response = view(request, pk=self.dev_team.pk)
        response.render()
        member = Member.objects.filter(team=self.dev_team, username=username)
        self.assertEqual(member.count(), 1, '(Exactly one) Member should\'ve been created')
        placeholder = PlayerPlaceholder.objects.filter(member=member[0], email=email)
        self.assertTrue(placeholder.exists(), 'Player placeholder should\'ve been created')
        self.assertNotEqual(member[0].activation_code, '', 'Activation code should be set')
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            'expected HTTP 201 - Created'
        )
