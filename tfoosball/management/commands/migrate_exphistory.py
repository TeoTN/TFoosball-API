from django.core.management.base import BaseCommand
from tfoosball.models import ExpHistory, ExpHistoryLegacy, Member


class Command(BaseCommand):
    help = 'Migrates ExpHistory to use Member'

    def migrate_history(self):
        history = ExpHistoryLegacy.objects.all()
        for old in history:
            member = Member.objects.get(username=old.player.username[:14])
            eh = ExpHistory(
                player=member,
                match=old.match,
                exp=old.exp
            )
            eh.save()
            eh.date = old.date
            eh.save()

    def handle(self, *args, **options):
        self.migrate_history()
