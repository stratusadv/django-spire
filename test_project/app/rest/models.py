from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django_glue import Glue

from django_glue.access.access import GlueAccess

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.querysets import HistoryQuerySet

from test_project.app.rest.services.service import PirateService


class PirateQuerySet(HistoryQuerySet):
    def search(self, search_value: str | None) -> PirateQuerySet:
        if not search_value:
            return self
        return self.filter(
            models.Q(first_name__icontains=search_value)
            | models.Q(last_name__icontains=search_value)
            | models.Q(username__icontains=search_value)
            | models.Q(email__icontains=search_value)
        )


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class Pirate(ActivityMixin, HistoryModelMixin):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    username = models.CharField(max_length=150, unique=True)

    objects = PirateQuerySet().as_manager()
    services = PirateService()

    @Glue.Attribute(access=GlueAccess.CHANGE)
    def duplicate(self, request: WSGIRequest) -> dict:
        return self.services.factory.duplicate(request)

    def __str__(self) -> str:
        return self.username

    @property
    def name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Pirate'
        verbose_name_plural = 'Pirates'
        db_table = 'test_project_rest_pirate'

    class GlueMeta:
        attributes = [('services', GlueAccess.VIEW)]
        exposed_attributes = [('name', GlueAccess.VIEW)]
