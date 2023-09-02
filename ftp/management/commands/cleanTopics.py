from django.core.management.base import BaseCommand, CommandError
from ftp.models import RequestedTopic
from django.utils import timezone


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            help='number of days',
            nargs=1, type=int
        )
        parser.add_argument(
            '--hours',
            help='number of hours',
            nargs=1, type=int
        )
        parser.add_argument(
            '--minutes',
            help='number of minutes',
            nargs=1, type=int
        )

    def handle(self, *args, **options):
        days = 0
        minutes = 0
        hours = 0
        if options['days']:
            days = options['days'][0]
        if options['hours']:
            hours = options['hours'][0]
        if options['minutes']:
            minutes = options['minutes'][0]

        print(days, minutes, hours)
        topics = RequestedTopic._base_manager.filter(
            verified=False,
            created_at__lt=timezone.now()-timezone.timedelta(days=days,
                                                             hours=hours, minutes=minutes)
        )
        length = len(topics)
        topics.delete()

        self.stdout.write(self.style.SUCCESS(
            'Successfully deleted {}'.format(length)))
