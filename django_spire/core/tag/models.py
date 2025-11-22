from typing import Sequence, Self

from django.db import models
from django.utils.text import slugify

from django_spire.core.tag.querysets import TagQuerySet


class Tag(models.Model):
    name = models.SlugField(
        max_length=128,
        unique=True
    )

    objects = TagQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        name = kwargs.get('name')
        if name:
            kwargs['name'] = slugify(name)

        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

    @classmethod
    def add_tags(cls, tags: Sequence[Self]):
        cls.objects.bulk_create(
            tags,
            ignore_conflicts=True
        )

    class Meta:
        db_table = 'django_spire_core_tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
