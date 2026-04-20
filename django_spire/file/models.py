from __future__ import annotations

import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django_spire.file.queryset import FileQuerySet
from django_spire.file.utils import format_size
from django_spire.history.mixins import HistoryModelMixin


class File(HistoryModelMixin):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        editable=False,
        blank=True,
        null=True,
    )

    object_id = models.PositiveIntegerField(editable=False, blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    file = models.FileField(max_length=500)
    name = models.CharField(max_length=255, default='', editable=False)
    type = models.CharField(max_length=255, default='', editable=False)
    size = models.PositiveBigIntegerField(default=0, editable=False)

    related_field = models.CharField(max_length=50, default='', blank=True, editable=False)

    objects = FileQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    @property
    def formatted_size(self) -> str:
        return format_size(self.size)

    def to_dict(self) -> dict[str, str | int]:
        return {
            'name': self.name,
            'url': self.file.url,
            'id': self.id
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    class Meta:
        db_table = 'django_spire_file'
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
