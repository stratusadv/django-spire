from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from django_spire.contrib import Breadcrumbs
from django_spire.file.mixins import FileModelMixin
from django_spire.file.models import File
from django_spire.history.mixins import HistoryModelMixin

from test_project.apps.file import querysets
from test_project.apps.file.constants import (
    ATTACHMENTS_RELATED_FIELD,
    PROFILE_PICTURE_RELATED_FIELD,
)
from test_project.apps.file.services.service import FileExampleService


class FileExample(HistoryModelMixin, FileModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.FileExampleQuerySet().as_manager()
    services = FileExampleService()

    def __str__(self) -> str:
        return self.name

    @cached_property
    def attachments(self) -> list[File]:
        return list(
            self.files
            .active()
            .filter(related_field=ATTACHMENTS_RELATED_FIELD)
            .order_by('-created_datetime')
        )

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()

        crumbs.add_breadcrumb(
            'File',
            reverse('file:page:list')
        )

        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)

        if self.pk:
            crumbs.add_breadcrumb(
                str(self),
                reverse(
                    'file:page:detail',
                    kwargs={'pk': self.pk}
                )
            )

        return crumbs

    @cached_property
    def profile_picture(self) -> File | None:
        try:
            return (
                self.files
                .active()
                .filter(related_field=PROFILE_PICTURE_RELATED_FIELD)
                .latest('created_datetime')
            )
        except File.DoesNotExist:
            return None

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        db_table = 'test_project_file'
