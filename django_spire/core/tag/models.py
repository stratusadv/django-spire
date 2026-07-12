from __future__ import annotations

from typing import Sequence, Self

from django.db import models
from django.utils.text import slugify

from django_spire.core.tag.querysets import TagQuerySet


class Tag(models.Model):
    name = models.SlugField(max_length=128, unique=True)

    objects = TagQuerySet.as_manager()

    class Meta:
        db_table = 'django_spire_core_tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __init__(self, *args, **kwargs) -> None:
        name = str(kwargs.get('name'))
        if name:
            kwargs['name'] = slugify(name)

        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def add_tags(cls, tags: Sequence[Self]) -> None:
        cls.objects.bulk_create(tags, ignore_conflicts=True)

