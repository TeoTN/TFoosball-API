from django.core.management.base import BaseCommand
from tfoosball.models import Player, Member, PlayerPlaceholder, Team, Match
import datetime


class UserImporter:
    @staticmethod
    def create_member(username, email, team):
        member = Member.objects.create(team=team, username=username, is_accepted=True)
        try:
            player = Player.objects.get(email=email)
        except:
            PlayerPlaceholder.objects.create(member=member, email=email)
        else:
            member.player = player
            member.save()
        return member

    @staticmethod
    def get_member(line, team):
        db_id, username, email, *_ = line.split(' ')
        return db_id, UserImporter.create_member(username, email, team)

    @staticmethod
    def run(team):
        with open('data/users.txt') as file:
            members = dict(UserImporter.get_member(line, team) for line in file)
        return members


class MatchImporter:
    fields = ['red_def', 'red_att', 'blue_def', 'blue_att', 'red_score', 'blue_score', 'date']

    def __init__(self, team):
        self.members = UserImporter().run(team)

    def process_line(self, line):
        players = [self.members[id] for id in line[:4]]
        scores = [int(line[4]), int(line[5])]
        date = [datetime.datetime.strptime(line[6].rstrip(), "%Y-%m-%d %H:%M:%S")]
        match_data = {k: v for k, v in zip(self.fields, players + scores + date)}
        Match.objects.create(**match_data)

    def run(self):
        with open('data/games.txt') as file:
            for line in file:
                self.process_line(line.split(';'))


class Command(BaseCommand):

    def handle(self, *args, **options):
        team, _ = Team.objects.get_or_create(name='RKS Brajdol', domain='brajdol')
        mi = MatchImporter(team)
        mi.run()
