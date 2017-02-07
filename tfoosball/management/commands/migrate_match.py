from django.core.management.base import BaseCommand
from tfoosball.models import Member, MatchLegacy, Match


class Command(BaseCommand):
    help = 'Migrates Match to use Member'

    def migrate_matches(self):
        matches = MatchLegacy.objects.all()
        for old in matches:
            ra = Member.objects.get(username=old.red_att.username[:14])
            rd = Member.objects.get(username=old.red_def.username[:14])
            ba = Member.objects.get(username=old.blue_att.username[:14])
            bd = Member.objects.get(username=old.blue_def.username[:14])

            match = Match(
                red_att=ra, blue_att=ba,
                red_def=rd, blue_def=bd,
                red_score=old.red_score, blue_score=old.blue_score,
                points=old.points, status=old.status,
            )
            match.save()
            match.date = old.date
            match.save()

    def handle(self, *args, **options):
        self.migrate_matches()
