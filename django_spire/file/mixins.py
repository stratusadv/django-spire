from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation

from django.db import models


class FileModelMixin(models.Model):
    files = GenericRelation('file.File', editable=False)

    class Meta:
        abstract = True
