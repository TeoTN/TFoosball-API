from django.core.management.base import BaseCommand
from tfoosball.models import Match, ExpHistory, Member


class Command(BaseCommand):
    help = 'Deletes exp history and creates it from scratch'

    def delete_history(self):
        ExpHistory.objects.all().delete()

    def init_history(self):
        for member in Member.objects.exclude(player__isnull=True):
            ExpHistory.objects.create(player=member, exp=1000, date=member.player.date_joined, matches_played=0)
            member.exp = 1000
            member.save()

    def update_members_exp(self, match):
        for member in match.users[:2]:
            member.exp += match.points
            member.save()
        for member in match.users[2:]:
            member.exp -= match.points
            member.save()

    def create_history(self):
        for match in Match.objects.all().order_by('date'):
            self.update_members_exp(match)
            Match.create_exp_history(match)

    def handle(self, *args, **options):
        self.delete_history()
        self.init_history()
        self.create_history()
