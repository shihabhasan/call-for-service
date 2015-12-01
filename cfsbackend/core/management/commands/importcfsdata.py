from django.core.management.base import BaseCommand

from core.etl import ETL


class Command(BaseCommand):
    help = "Load CFS data."

    def add_arguments(self, parser):
        parser.add_argument('dir', nargs=1, type=str)

    def handle(self, *args, **options):
        etl = ETL(dir=options['dir'][0])
        etl.run()