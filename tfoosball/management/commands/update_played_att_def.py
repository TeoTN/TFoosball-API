from django.core.management.base import BaseCommand
from tfoosball.models import Match, Member


class Command(BaseCommand):
    help = 'Recounts members\' number of matches played on offence and on defence. Use wisely.'

    def clean_counter(self):
        for member in Member.objects.all():
            member.offence_played = 0
            member.defence_played = 0
            member.save()

    def update_attackers(self, players):
        for player in players:
            player.offence_played += 1
            player.save()

    def update_defenders(self, players):
        for player in players:
            player.defence_played += 1
            player.save()

    def update_match_players(self, match):
        self.update_attackers(match.attackers)
        self.update_defenders(match.defenders)

    def update_players(self):
        matches = Match.objects.all()
        for m in matches:
            self.update_match_players(m)

    def handle(self, *args, **options):
        self.clean_counter()
        self.update_players()
