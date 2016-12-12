from django.core.management.base import BaseCommand
from tfoosball.models import Player
import users


class Command(BaseCommand):
    help = 'Populates db with users from tfoosball/fixtures/users.json'

    def upload_users():
        with open('tfoosball/fixtures/users.json', 'r') as fh:
             users = json.load(fh)

        for user in users:
            Player.objects.create_user(**user)

    def handle(self, *args, **options):
        self.upload_users()
