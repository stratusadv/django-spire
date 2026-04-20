from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.file.models import File
from django_spire.file.services import copy_files_to_instance


class FileModelMixin(models.Model):
    files = GenericRelation(File, editable=False)

    class Meta:
        abstract = True

    def copy_files_to(self, target: models.Model) -> list[File]:
        return copy_files_to_instance(self.files.active(), target)
