from django.core.management.base import BaseCommand
from tfoosball.models import Match, Member


class Command(BaseCommand):
    help = 'Recalculates members\' number of matches played and won on offence and on defence. Use wisely.'

    def clear_stats(self, member):
        member.offence_played = 0
        member.defence_played = 0
        member.offence_won = 0
        member.defence_won = 0
        member.win_streak = 0
        member.lose_streak = 0
        member.curr_win_streak = 0
        member.curr_lose_streak = 0
        member.exp = 1000

    def update_member(self, member):
        matches = member.get_latest_matches().order_by('date')
        for match in matches:
            _, winner = match.calculate_points()
            red_result, blue_result = match.get_team_result(winner)
            if member == match.red_att:
                member.after_match_update(match.points, red_result, True, save=False)
            elif member == match.red_def:
                member.after_match_update(match.points, red_result, False, save=False)
            elif member == match.blue_att:
                member.after_match_update(-match.points, blue_result, True, save=False)
            elif member == match.blue_def:
                member.after_match_update(-match.points, blue_result, False, save=False)
        member.save()

    def handle(self, *args, **options):
        for member in Member.objects.all():
            self.clear_stats(member)
            self.update_member(member)
