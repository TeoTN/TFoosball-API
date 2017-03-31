from django.test import TestCase
from tfoosball.models import Match, Member


class MatchModelTest(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json', 'matches.json']

    def setUp(self):
        members = Member.objects.filter(team=4).order_by('-exp')[:4]
        self.members_0 = {'red_att': members[0], 'red_def': members[1], 'blue_att': members[2], 'blue_def': members[3]}
        self.members_1 = {'red_att': members[2], 'red_def': members[3], 'blue_att': members[0], 'blue_def': members[1]}

    def test_10_0(self):
        match = Match(red_score=10, blue_score=0, **self.members_0)
        points, winner = match.calculate_points()
        self.assertGreaterEqual(points, 0)
        self.assertEqual(winner, 1)

    def test_0_10(self):
        match = Match(red_score=0, blue_score=10, **self.members_0)
        points, winner = match.calculate_points()
        self.assertLessEqual(points, 0)
        self.assertEqual(winner, 0)

    def test_equal_tie(self):
        self.members_0['blue_def'].exp = 1034
        self.assertEqual(self.members_0['red_att'].exp + self.members_0['red_def'].exp,
                         self.members_0['blue_att'].exp + self.members_0['blue_def'].exp)

        match = Match(red_score=10, blue_score=10, **self.members_0)
        points, winner = match.calculate_points()
        self.assertEqual(points, 0)
        self.assertEqual(winner, 0.5)

    def test_unequal_tie(self):
        self.assertNotEqual(self.members_0['red_att'].exp + self.members_0['red_def'].exp,
                            self.members_0['blue_att'].exp + self.members_0['blue_def'].exp)

        match = Match(red_score=10, blue_score=10, **self.members_0)
        points, winner = match.calculate_points()
        self.assertEqual(winner, 0.5)

    def test_tie_bias(self):
        match = Match(red_score=10, blue_score=10, **self.members_0)
        points_0, _ = match.calculate_points()
        match_1 = Match(red_score=10, blue_score=10, **self.members_1)
        points_1, _ = match_1.calculate_points()
        self.assertEqual(points_1, -points_0)

    def test_bias(self):
        match = Match(red_score=10, blue_score=0, **self.members_0)
        points_0, _ = match.calculate_points()
        match_1 = Match(red_score=0, blue_score=10, **self.members_1)
        points_1, _ = match_1.calculate_points()
        self.assertEqual(points_1, -points_0)
