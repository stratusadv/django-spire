from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a Spire app.'

    def handle(self, *args, **options):
        self.stdout.write('hello from Spire app')
