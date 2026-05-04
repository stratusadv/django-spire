from __future__ import annotations

from django.db import models

from django_spire.contrib.sync.django.mixin import SyncableMixin


class SyncTestTag(models.Model):
    label = models.CharField(max_length=100)

    class Meta:
        app_label = 'sync_tests'

    def __str__(self) -> str:
        return 'test'


class SyncTestModel(SyncableMixin):
    name = models.CharField(max_length=255)
    value = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    tags = models.ManyToManyField(SyncTestTag, blank=True)

    class Meta:
        app_label = 'sync_tests'


class SyncTestSimpleModel(SyncableMixin):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'sync_tests'
