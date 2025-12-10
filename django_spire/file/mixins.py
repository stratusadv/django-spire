from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.file.models import File
from django_spire.file.tools import copy_files_from_source_to_target_model_object


class FileModelMixin(models.Model):
    files = GenericRelation(File, editable=False)

    def copy_files_to_target_model_object(self, target: models.Model) -> list[File]:
        # TODO: Move to File Service
        return copy_files_from_source_to_target_model_object(source=self, target=target)

    class Meta:
        abstract = True
