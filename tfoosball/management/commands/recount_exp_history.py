from django.core.management.base import BaseCommand
from tfoosball.models import Player, Match, ExpHistory


class Command(BaseCommand):
    help = 'Deletes exp history and creates it from scratch'

    def delete_history(self):
        ExpHistory.objects.all().delete()

    def init_history(self):
        for player in Player.objects.all():
            ExpHistory(player=player, date=player.date_joined, exp=1000).save()
            player.exp = 1000
            player.save()

    def create_history(self):
        def get_points(match, role):
            return match.points if role == 'red' else -match.points

        for match in Match.objects.all().order_by('date'):
            match.red_att.exp += get_points(match, 'red')
            match.red_att.save()
            eh = ExpHistory(player=match.red_att, date=match.date, exp=match.red_att.exp, match=match)
            eh.save()
            eh.date = match.date
            eh.save()

            match.red_def.exp += get_points(match, 'red')
            match.red_def.save()
            eh = ExpHistory(player=match.red_def, date=match.date, exp=match.red_def.exp, match=match)
            eh.save()
            eh.date = match.date
            eh.save()

            match.blue_att.exp += get_points(match, 'blue')
            match.blue_att.save()
            eh = ExpHistory(player=match.blue_att, date=match.date, exp=match.blue_att.exp, match=match)
            eh.save()
            eh.date = match.date
            eh.save()

            match.blue_def.exp += get_points(match, 'blue')
            match.blue_def.save()
            eh = ExpHistory(player=match.blue_def, date=match.date, exp=match.blue_def.exp, match=match)
            eh.save()
            eh.date = match.date
            eh.save()

    def handle(self, *args, **options):
        self.delete_history()
        self.init_history()
        self.create_history()
