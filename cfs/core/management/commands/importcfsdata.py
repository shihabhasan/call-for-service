from django.core.management.base import BaseCommand

from core.etl import ETL


class Command(BaseCommand):
    help = "Load CFS data."

    def add_arguments(self, parser):
        parser.add_argument('dir', type=str, help='Directory containing '
                'the files to load')
        parser.add_argument('--reset', type=bool, default=False,
                help='Whether to clear the database before loading '
                '(defaults to False)')

    def handle(self, *args, **options):
        etl = ETL(dir=options['dir'], reset=options['reset'])
        etl.run()
