from __future__ import annotations

from django.db import models

from django_spire.core.tag.models import Tag
from django_spire.core.tag.tools import simplify_and_weight_tag_set_to_dict, simplify_tag_set


class TagModelMixin(models.Model):
    tags = models.ManyToManyField(Tag, related_name='+', null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    @property
    def tag_set(self) -> set[str]:
        return set(self.tags.values_list('name', flat=True))

    @property
    def simplified_tag_set(self) -> set[str]:
        return simplify_tag_set(self.tag_set)

    @property
    def simplified_and_weighted_tag_dict(self) -> dict[str, int]:
        return simplify_and_weight_tag_set_to_dict(self.tag_set)
