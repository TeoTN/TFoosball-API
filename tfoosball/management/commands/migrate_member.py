from django.core.management.base import BaseCommand
from tfoosball.models import Player, Member, Team
from django.forms.models import model_to_dict


class Command(BaseCommand):
    help = 'Creates a team and migrates Player data to Member model'

    def create_team(self, name):
        self.name = name
        self.domain = name.replace(' ', '').lower()
        return Team.objects.get_or_create(name=self.name, domain=self.domain)[0]

    def add_arguments(self, parser):
        parser.add_argument(
            '--teamname',
            dest='teamname',
            default='Unknown Team'
        )

    def migrate_players(self):
        players = Player.objects.all()
        fields = ['exp', 'offence', 'defence', 'played', 'win_streak', 'curr_win_streak',
                  'lose_streak', 'curr_lose_streak', 'lowest_exp', 'highest_exp']

        for player in players:
            data = model_to_dict(player, fields=fields)
            Member.objects.create(**data, team=self.team, player=player, username=player.username[:14])

    def handle(self, *args, **options):
        self.team = self.create_team(options['teamname'])
        self.migrate_players()
