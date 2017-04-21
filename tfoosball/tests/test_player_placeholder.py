from django.core.exceptions import ValidationError
from django.test import TestCase
from tfoosball.models import PlayerPlaceholder, Member


class MatchModelTest(TestCase):
    fixtures = ['players.json', 'teams.json', 'members.json', 'player_placeholder.json']

    def setUp(self):
        self.placeholder = PlayerPlaceholder.objects.get(id=1)

    def test_unique_fail(self):
        member = Member.objects.get(id=9)
        self.assertEqual(member.team, self.placeholder.member.team)
        with self.assertRaises(ValidationError):
            PlayerPlaceholder.objects.create(email=self.placeholder.email, member=member)

    def test_unique(self):
        member = Member.objects.get(id=15)
        self.assertNotEqual(member.team, self.placeholder.member.team)
        n = PlayerPlaceholder.objects.create(email=self.placeholder.email, member=member)
        self.assertEqual(n.email, self.placeholder.email)
