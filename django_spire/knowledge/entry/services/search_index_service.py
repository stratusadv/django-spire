from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import connection

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class EntrySearchIndexService(BaseDjangoModelService['Entry']):
    obj: Entry

    def rebuild_search_index(self):
        words = []

        words.append(self.obj.name)

        if self.obj.current_version is None:
            return

        for block in self.obj.current_version.blocks.active().order_by('order'):
            text = block.render_to_text().strip()

            if text and text != '\n':
                words.append(text)

        words.extend(
            tag.name
            for tag in self.obj.tags.all()
        )

        self.obj._search_text = '\n'.join(words)
        self.obj.save(update_fields=['_search_text'])

        if connection.vendor == 'postgresql':
            from django.contrib.postgres.search import SearchVector

            self.obj_class.objects.filter(pk=self.obj.pk).update(
                _search_vector=(
                    SearchVector('name', weight='A', config='english') +
                    SearchVector('_search_text', weight='B', config='english')
                )
            )

    @classmethod
    def rebuild_all_search_indexes(cls):
        from django_spire.knowledge.entry.models import Entry

        entries = (
            Entry.objects
            .active()
            .has_current_version()
            .select_related('current_version')
            .prefetch_related('current_version__blocks', 'tags')
        )

        for entry in entries.iterator(chunk_size=100):
            entry.services.search_index.rebuild_search_index()
