from django.test import TestCase
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status
from api.views import MemberViewSet
from api.serializers import MemberSerializer
from tfoosball.models import Player, Team, Member
import json

factory = APIRequestFactory()


class TeamMembersEndpointTestCase(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json']

    def setUp(self):
        self.admin_user = Player.objects.get(username='admin')
        self.dummy_user = Player.objects.get(pk=11)
        self.dev_team = Team.objects.get(domain='dev')
        self.member = Member.objects.get(player_id=8, team__domain='dev')
        self.fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'exp', 'played', 'att_ratio', 'def_ratio',
            'win_ratio', 'win_streak', 'lose_streak', 'curr_lose_streak', 'curr_win_streak', 'lowest_exp',
            'highest_exp', 'exp_history',
        )

    def test_get_list(self):
        members = Member.objects.filter(team=self.dev_team)
        request = factory.get('/api/teams/dev/members/')
        force_authenticate(request, user=self.admin_user)
        view = MemberViewSet.as_view({'get': 'list'})
        response = view(request, parent_lookup_team='dev')
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(len(response_data), members.count(), 'expected correct number of dev team members')

    def test_get_item(self):
        request = factory.get('/api/teams/dev/members/8/')
        force_authenticate(request, user=self.admin_user)
        view = MemberViewSet.as_view({'get': 'retrieve'})
        response = view(request, parent_lookup_team='dev', pk='8')
        response.render()
        expected_data = MemberSerializer(self.member).data
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        for rk, ek in zip(response.data.keys(), expected_data.keys()):
            self.assertEqual(str(response.data[rk]), str(expected_data[ek]), 'expected correct member data')

    def test_discard(self):
        request = factory.delete('/api/teams/{0}/members/9/'.format(self.dev_team.domain))
        force_authenticate(request, user=self.admin_user)
        view = MemberViewSet.as_view({'delete': 'destroy'})
        response = view(request, parent_lookup_team='dev', pk='9')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'expected HTTP 204 - No content')

    def test_discard_not_admin(self):
        request = factory.delete('/api/teams/{0}/members/10/'.format(self.dev_team.domain))
        force_authenticate(request, user=self.dummy_user)
        view = MemberViewSet.as_view({'delete': 'destroy'})
        response = view(request, parent_lookup_team='dev', pk='10')
        response.render()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'expected HTTP 403 - Forbidden')

    def test_get_pending(self):
        members = Member.objects.filter(team=self.dev_team, is_accepted=False)
        request = factory.get('/api/teams/dev/members/?is_accepted=false')
        force_authenticate(request, user=self.admin_user)
        view = MemberViewSet.as_view({'get': 'list'})
        response = view(request, parent_lookup_team='dev')
        response.render()
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'expected HTTP 200')
        self.assertEqual(len(response_data), members.count(), 'expected correct number of dev team unaccepted members')
