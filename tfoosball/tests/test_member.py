from django.test import TestCase
from django.db.utils import IntegrityError
from tfoosball.models import Member


class MatchModelTest(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json']

    def setUp(self):
        self.members = Member.objects.filter(team=4)
        self.dummy_member = self.members.get(username='lfields7')

    def test0(self):
        member = self.members.get(username='kscott8')
        member.username = self.dummy_member.username
        with self.assertRaises(IntegrityError):
            member.save()
