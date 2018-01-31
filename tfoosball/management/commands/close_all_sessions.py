from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = 'WARNING! This command closes all opened sessions. Users will be logged out.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            dest='force',
            default=False,
            action='store_true',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        if force:
            Session.objects.all().delete()
        else:
            print('''
            WARNING! This command will shut down all opened users sessions. They will be logged out.
            If you are sure that you want to perform that call this command with `--force`.
            ''')
