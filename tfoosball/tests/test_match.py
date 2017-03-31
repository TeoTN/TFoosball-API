from django.test import TestCase
from tfoosball.models import Match, Member


class MatchModelTest(TestCase):
    fixtures = ['teams.json', 'players.json', 'members.json']

    def setUp(self):
        members = Member.objects.filter(team=4).order_by('-exp')[:4]
        self.members_0 = {'red_att': members[0], 'red_def': members[1], 'blue_att': members[2], 'blue_def': members[3]}
        self.members_1 = {'red_att': members[2], 'red_def': members[3], 'blue_att': members[0], 'blue_def': members[1]}

    def test_below_0(self):
        match = Match(red_score=10, blue_score=-5, **self.members_0)
        with self.assertRaises(AssertionError):
            match.save()

    def test_above_10(self):
        match = Match(red_score=15, blue_score=10, **self.members_0)
        points, winner = match.calculate_points()
        self.assertGreaterEqual(points, 0)
        self.assertEqual(winner, Match.RED)

    def test_10_0(self):
        match = Match(red_score=10, blue_score=0, **self.members_0)
        points, winner = match.calculate_points()
        self.assertGreaterEqual(points, 0)
        self.assertEqual(winner, Match.RED)

    def test_0_10(self):
        match = Match(red_score=0, blue_score=10, **self.members_0)
        points, winner = match.calculate_points()
        self.assertLessEqual(points, 0)
        self.assertEqual(winner, Match.BLUE)

    def test_equal_tie(self):
        self.members_0['blue_def'].exp = 1034
        self.assertEqual(self.members_0['red_att'].exp + self.members_0['red_def'].exp,
                         self.members_0['blue_att'].exp + self.members_0['blue_def'].exp)
        for score in range(1, 11):
            match = Match(red_score=score, blue_score=score, **self.members_0)
            points, winner = match.calculate_points()
            self.assertEqual(points, 0)
            self.assertEqual(winner, Match.TIE)

    def test_unequal_tie(self):
        self.assertNotEqual(self.members_0['red_att'].exp + self.members_0['red_def'].exp,
                            self.members_0['blue_att'].exp + self.members_0['blue_def'].exp)

        for score in range(1, 11):
            match = Match(red_score=score, blue_score=score, **self.members_0)
            _, winner = match.calculate_points()
            self.assertEqual(winner, Match.TIE)

    def test_bias(self):
        for score in range(1, 11):
            match = Match(red_score=10, blue_score=score, **self.members_0)
            points_0, _ = match.calculate_points()
            match_1 = Match(red_score=score, blue_score=10, **self.members_1)
            points_1, _ = match_1.calculate_points()
            self.assertEqual(points_0, -points_1)

    def test_update_exp_red_wins(self):
        match = Match(red_score=8, blue_score=10, **self.members_0)
        exp_0 = (
            self.members_0['red_att'].exp, self.members_0['red_def'].exp,
            self.members_0['blue_att'].exp, self.members_0['blue_def'].exp)
        match.save()
        points = match.points
        exp_1 = (
            self.members_0['red_att'].exp, self.members_0['red_def'].exp,
            self.members_0['blue_att'].exp, self.members_0['blue_def'].exp)

        self.assertEqual(exp_0[0] + points, exp_1[0])
        self.assertEqual(exp_0[1] + points, exp_1[1])
        self.assertEqual(exp_0[2] - points, exp_1[2])
        self.assertEqual(exp_0[3] - points, exp_1[3])

    def test_update_exp_blue_wins(self):
        match = Match(red_score=10, blue_score=8, **self.members_0)
        exp_0 = (
            self.members_0['red_att'].exp, self.members_0['red_def'].exp,
            self.members_0['blue_att'].exp, self.members_0['blue_def'].exp)
        match.save()
        points = match.points
        exp_1 = (
            self.members_0['red_att'].exp, self.members_0['red_def'].exp,
            self.members_0['blue_att'].exp, self.members_0['blue_def'].exp)

        self.assertEqual(exp_0[0] + points, exp_1[0])
        self.assertEqual(exp_0[1] + points, exp_1[1])
        self.assertEqual(exp_0[2] - points, exp_1[2])
        self.assertEqual(exp_0[3] - points, exp_1[3])
