from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from django_spire.auth.user.models import AuthUser
from django_spire.history.mixins import HistoryModelMixin
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
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
        choices=EntryVersionStatusChoices,
        default=EntryVersionStatusChoices.DRAFT
    )

    objects = EntryVersionQuerySet.as_manager()
    services = EntryVersionService()

    def is_published(self) -> bool:
        return self.status == EntryVersionStatusChoices.PUBLISHED

    @property
    def view_url(self) -> str:
        site = Site.objects.get_current() if not settings.DEBUG else ''
        path = reverse(
            'django_spire:knowledge:entry:version:page:detail',
            kwargs={'pk': self.pk},
        )[1:]
        return f'{site}/{path}'

    class Meta:
        verbose_name = 'Entry Version'
        verbose_name_plural = 'Entry Versions'
        db_table = 'django_spire_knowledge_entry_version'
