from django.db import models
from django.utils.timezone import now

from django_spire.auth.user.models import AuthUser
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.entry.version.choices import EntryVersionTypeChoices
from django_spire.knowledge.entry.version.querysets import EntryVersionQuerySet
from django_spire.knowledge.entry.version.services.service import EntryVersionService


class EntryVersion(HistoryModelMixin):
    entry = models.ForeignKey(
        'Entry',
        on_delete=models.CASCADE,
        related_name='versions',
        related_query_name='version'
    )
    author = models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='entry_versions',
        related_query_name='entry_version'
    )
    published_datetime = models.DateTimeField(blank=True, null=True)
    last_edit_datetime = models.DateTimeField(default=now)

    status = models.CharField(
        max_length=32,
        choices=EntryVersionTypeChoices,
        default=EntryVersionTypeChoices.DRAFT
    )

    objects = EntryVersionQuerySet.as_manager()
    services = EntryVersionService()

    def is_published(self) -> bool:
        return self.status == EntryVersionTypeChoices.PUBLISHED

    class Meta:
        verbose_name = 'Entry Version'
        verbose_name_plural = 'Entry Versions'
        db_table = 'django_spire_knowledge_entry_version'
