from __future__ import annotations

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a Spire app.'

    def handle(self, *args, **options) -> None:
        self.stdout.write('hello from Spire app')
