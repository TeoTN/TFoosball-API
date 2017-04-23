from django.core.management.base import BaseCommand
from tfoosball.models import Player, Team, Member
import json


class Command(BaseCommand):
    help = 'Populates db with users from tfoosball/fixtures/users.json'

    def init_team(self):
        self.team, created = Team.objects.get_or_create(name='Developer Team', domain='dev')

    def upload_users(self):
        with open('tfoosball/fixtures/users.json', 'r') as fh:
            users = json.load(fh)

        for user in users:
            player = Player.objects.create_user(**user)
            Member.objects.get_or_create(team=self.team, player=player, username=player.username[:14])

    def handle(self, *args, **options):
        self.init_team()
        self.upload_users()
