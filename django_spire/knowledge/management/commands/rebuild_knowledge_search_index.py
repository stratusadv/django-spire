from __future__ import annotations

from django.core.management.base import BaseCommand

from django_spire.knowledge.entry.models import Entry


class Command(BaseCommand):
    help = 'Rebuilds the search index for all knowledge base entries.'

    def handle(self, *args, **options):
        self.stdout.write('Rebuilding search indexes...')

        Entry.services.search_index.rebuild_all_search_indexes()

        self.stdout.write(self.style.SUCCESS('Search indexes rebuilt successfully.'))
