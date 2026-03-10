from django.db import models

from django_spire.api.choices import ApiPermissionChoices
from django_spire.api.querysets import ApiAccessQuerySet
from django_spire.api.tools import hash_string
from django_spire.history.mixins import HistoryModelMixin


class ApiAccess(HistoryModelMixin):
    name = models.CharField(max_length=128)
    hashed_key = models.CharField(max_length=128, editable=False)
    key_hint = models.CharField(max_length=16, editable=False)
    permission = models.PositiveSmallIntegerField(
        default=ApiPermissionChoices.VIEW,
        choices=ApiPermissionChoices,
    )

    objects = ApiAccessQuerySet.as_manager()  # ty:ignore[missing-argument]

    def __str__(self) -> str:
        return f'{self.name} - {self.key_hint}'

    def set_key_and_save(self, raw_key: str) -> None:
        self.hashed_key = hash_string(raw_key)
        self.key_hint = raw_key[:4] + ' ... ' + raw_key[-4:]
        self.save()

    class Meta:
        verbose_name = 'API Access'
        verbose_name_plural = 'API Accesses'
        db_table = 'django_spire_api_access'
        ordering = ('name',)
