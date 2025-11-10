from django.db import models
from django.db.models import QuerySet

from django_spire.core.tags.models import Tag


class TagsModelMixin(models.Model):
    aggregated_tags = models.ManyToManyField(Tag, related_name='+')
    tags = models.ManyToManyField(Tag, related_name='+')

    class Meta:
        abstract = True

    @property
    def aggregated_tag_set(self) -> set[str]:
        return set(self.aggregated_tags.values_list('name', flat=True))

    @property
    def tag_set(self) -> set[str]:
        return set(self.tags.values_list('name', flat=True))

    def add_tags_from_tag_set(self, tag_set: set[str], add_to_aggregated: bool = True):
        self._update_global_tags_from_set(tag_set)

        tag_objects = Tag.objects.in_tag_set(tag_set)

        self.tags.add(*tag_objects)

        if add_to_aggregated:
            self.aggregated_tags.add(*tag_objects)

    def add_tags_to_aggregated_from_tag_set(self, tag_set: set[str]):
        self._update_global_tags_from_set(tag_set)

        self.aggregated_tags.add(*Tag.objects.in_tag_set(tag_set))

    # @staticmethod
    # def _clean_tag_set(tag_set: set[str]) -> set[str]:
    #     return set(map(slugify, tag_set))

    def clear_tags(self):
        self.aggregated_tags.remove(*self.tags.all())
        self.tags.clear()

    def clear_aggregated_tags(self):
        self.aggregated_tags.clear()

    def get_and_set_aggregated_tag_set(self, tag_set: set[str] | None = None):
        if tag_set:
            self.add_tags_to_aggregated_from_tag_set(tag_set)

        return self.aggregated_tag_set

    def get_matching_tags_from_tag_set(self, tag_set: set[str]) -> QuerySet:
        return self.tags.in_tag_set(tag_set)

    def get_matching_tags_in_aggregated_from_tag_set(self, tag_set: set[str]) -> QuerySet:
        return self.aggregated_tags.in_tag_set(tag_set)

    def get_matching_tags_percentage_from_tag_set(self, tag_set: set[str]) -> float:
        return (
            len(self.get_matching_tags_from_tag_set(tag_set)) / len(tag_set)
            if tag_set
            else 0.0
        )

    def get_matching_tags_in_aggregated_percentage_from_tag_set(self, tag_set: set[str]) -> float:
        return (
            len(self.get_matching_tags_in_aggregated_from_tag_set(tag_set)) / len(tag_set)
            if tag_set
            else 0.0
        )

    def get_matching_model_tags_percentage_from_tag_set(self, tag_set: set[str]) -> float:
        return (
            len(self.get_matching_tags_from_tag_set(tag_set)) / len(self.tags.all())
            if self.tags
            else 0.0
        )

    def get_matching_model_tags_in_aggregated_percentage_from_tag_set(
        self, tag_set: set[str]
    ) -> float:
        return (
            len(self.get_matching_tags_in_aggregated_from_tag_set(tag_set))
            / len(self.aggregated_tags.all())
            if self.aggregated_tags
            else 0.0
        )

    def has_tag_set(self, tag_set: set[str]) -> bool:
        return len(self.get_matching_tags_from_tag_set(tag_set)) == len(tag_set)

    def has_tag_set_in_aggregated(self, tag_set: set[str]) -> bool:
        return len(self.get_matching_tags_in_aggregated_from_tag_set(tag_set)) == len(tag_set)

    def remove_tag_set(self, tag_set: set[str], remove_from_aggregated: bool = False):
        tag_objects = Tag.objects.in_tag_set(tag_set)

        self.tags.remove(*tag_objects)

        if remove_from_aggregated:
            self.aggregated_tags.remove(*tag_objects)

    def remove_tag_set_from_aggregated(self, tag_set: set[str]):
        self.aggregated_tags.remove(*Tag.objects.in_tag_set(tag_set))

    def set_tags_from_tag_set(self, tag_set: set[str], add_to_aggregated: bool = True, also_set_aggregated: bool = False):
        self._update_global_tags_from_set(tag_set)

        tag_objects = Tag.objects.in_tag_set(tag_set)
        self.tags.set(tag_objects)

        if add_to_aggregated:
            self.aggregated_tags.add(*tag_objects)

        if also_set_aggregated:
            self.aggregated_tags.set(tag_objects)

    def set_tags_in_aggregated_from_tag_set(self, tag_set: set[str]):
        self._update_global_tags_from_set(tag_set)

        self.aggregated_tags.set(Tag.objects.in_tag_set(tag_set))

    @staticmethod
    def _update_global_tags_from_set(tag_set: set[str]):
        Tag.add_tags([Tag(name=tag) for tag in tag_set])
