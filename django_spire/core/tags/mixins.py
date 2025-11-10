from django.db import models
from django.db.models import QuerySet

from django_spire.core.tags.models import Tag
from django_spire.core.tags import tools


class TagsModelMixin(models.Model):
    tags = models.ManyToManyField(Tag, related_name='+', null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    @property
    def tag_set(self) -> set[str]:
        return set(self.tags.values_list('name', flat=True))

    @property
    def tag_set_simplified(self) -> set[str]:
        simplified_tag_words = []

        for tag in self.tag_set:
            tag_words = tag.split('-')
            simplified_tag_words.extend(tag_words)

        return set(simplified_tag_words)

    def add_tags_from_tag_set(self, tag_set: set[str]):
        self._update_global_tags_from_set(tag_set)

        self.tags.add(*Tag.objects.in_tag_set(tag_set))

    def clear_tags(self):
        self.tags.clear()

    def get_matching_tags_from_tag_set(self, tag_set: set[str]) -> QuerySet:
        return self.tags.in_tag_set(tag_set)

    def get_matching_percentage_of_tag_set(self, tag_set: set[str]) -> float:
        return tools.get_matching_a_percentage_from_tag_sets(tag_set, self.tag_set)

    def get_matching_percentage_of_model_tags_from_tag_set(self, tag_set: set[str]) -> float:
        return tools.get_matching_b_percentage_from_tag_sets(tag_set, self.tag_set)

    def has_tags_in_tag_set(self, tag_set: set[str]) -> bool:
        return self.tag_set.issuperset(tag_set)

    def remove_tags_by_tag_set(self, tag_set: set[str]):
        tag_objects = Tag.objects.in_tag_set(tag_set)

        self.tags.remove(*tag_objects)

    def set_tags_from_tag_set(self, tag_set: set[str]):
        self._update_global_tags_from_set(tag_set)

        tag_objects = Tag.objects.in_tag_set(tag_set)
        self.tags.set(tag_objects)

    @staticmethod
    def _update_global_tags_from_set(tag_set: set[str]):
        Tag.add_tags([Tag(name=tag) for tag in tag_set])
