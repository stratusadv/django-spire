from __future__ import annotations

import json

from django.contrib.contenttypes.models import ContentType

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from django_spire.file.queryset import FileQuerySet
from django_spire.history.mixins import HistoryModelMixin


class File(HistoryModelMixin):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False, blank=True, null=True)
    object_id = models.PositiveIntegerField(editable=False, blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    file = models.FileField(max_length=500)
    name = models.CharField(max_length=255, default='', editable=False)
    type = models.CharField(max_length=255, default='', editable=False)
    size = models.CharField(max_length=64, default='', editable=False)

    related_field = models.CharField(max_length=3, null=True, blank=True, editable=False)

    objects = FileQuerySet.as_manager()

    def __str__(self):
        return self.name

    def to_dict(self) -> dict[str, str]:
        return {
            'name': self.name,
            'url': self.file.url,
            'id': self.id
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    class Meta:
        db_table = 'spire_file'
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

