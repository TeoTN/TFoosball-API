from django.test import TestCase
from django.db.utils import IntegrityError
from tfoosball.models import Member, PlayerPlaceholder


class MemberModelTest(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json']

    def setUp(self):
        self.team_id = 4
        self.new_team_id = 5
        self.dummy_member = Member.objects.get(username='lfields7', team=self.team_id)

    def test_unique_username(self):
        member = Member.objects.get(username='kscott8', team=self.dummy_member.team)
        member.username = self.dummy_member.username
        with self.assertRaises(IntegrityError):
            member.save()

    def test_create_member(self):
        username = 'mr dummy'
        _, is_placeholder = Member.create_member(username, self.dummy_member.player.email, self.new_team_id)
        member = Member.objects.get(username=username, team=self.new_team_id)
        self.assertEqual(member.player, self.dummy_member.player)
        with self.assertRaises(PlayerPlaceholder.DoesNotExist):
            PlayerPlaceholder.objects.get(member=member)
        self.assertFalse(is_placeholder)

    def test_create_existing_member(self):
        username = 'mr dummy'
        _, is_placeholder = Member.create_member(username, self.dummy_member.player.email, self.new_team_id)
        member = Member.objects.get(username=username, team=self.new_team_id)
        self.assertEqual(member.player, self.dummy_member.player)
        with self.assertRaises(PlayerPlaceholder.DoesNotExist):
            PlayerPlaceholder.objects.get(member=member)
        self.assertFalse(is_placeholder)
        with self.assertRaises(IntegrityError):
            Member.create_member(username, self.dummy_member.player.email, self.new_team_id)

    def test_create_member_placeholder(self):
        email = 'newbie@mail.com'
        member, is_placeholder = Member.create_member('newbie', email, self.new_team_id)
        self.assertIsNone(member.player)
        placeholder = PlayerPlaceholder.objects.get(member=member)
        self.assertEqual(placeholder.email, email)
        self.assertTrue(is_placeholder)

    def test_create_existing_member_placeholder(self):
        email = 'newbie@mail.com'
        member, is_placeholder = Member.create_member('newbie', email, self.new_team_id)
        self.assertIsNone(member.player)
        placeholder = PlayerPlaceholder.objects.get(member=member)
        self.assertEqual(placeholder.email, email)
        self.assertTrue(is_placeholder)
        with self.assertRaises(IntegrityError):
            Member.create_member('newbie', email, self.new_team_id)

