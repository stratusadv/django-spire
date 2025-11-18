from abc import abstractmethod, ABC
from typing import Generic

from django.db.models import QuerySet

from django_spire.contrib.constructor.django_model_constructor import TypeDjangoModel
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.core.tag import tools
from django_spire.core.tag.models import Tag
from django_spire.core.tag.tools import get_score_percentage_from_tag_set_weighted


class BaseTagService(
    BaseDjangoModelService[TypeDjangoModel],
    ABC,
    Generic[TypeDjangoModel]
):
    obj: TypeDjangoModel

    @abstractmethod
    def process_and_set_tags(self):
        raise NotImplementedError

    def add_tags_from_tag_set(self, tag_set: set[str]):
        self._update_global_tags_from_set(tag_set)

        self.obj.tags.add(*Tag.objects.in_tag_set(tag_set))

    def clear_tags(self):
        self.obj.tags.clear()

    def get_matching_tags_from_tag_set(self, tag_set: set[str]) -> QuerySet:
        return self.obj.tags.in_tag_set(tag_set)

    def get_matching_percentage_of_tag_set(self, tag_set: set[str]) -> float:
        return tools.get_matching_a_percentage_from_tag_sets(tag_set, self.obj.tag_set)

    def get_matching_percentage_of_model_tags_from_tag_set(self, tag_set: set[str]) -> float:
        return tools.get_matching_b_percentage_from_tag_sets(tag_set, self.obj.tag_set)

    def get_score_percentage_from_tag_set_weighted(self, tag_set: set[str]) -> float:
        return get_score_percentage_from_tag_set_weighted(
            tag_set_actual=tag_set,
            tag_set_reference=self.obj.tag_set
        )

    def get_simplified_and_weighted_tag_dict_above_minimum(self, minimum_weight: int = 1) -> dict[str, int]:
        above_minimum_tag_dict = self.obj.simplified_and_weighted_tag_dict

        return {
            tag: weight
            for tag, weight in above_minimum_tag_dict.items()
            if weight >= minimum_weight
        }

    def has_tags_in_tag_set(self, tag_set: set[str]) -> bool:
        return self.obj.tag_set.issuperset(tag_set)

    def remove_tags_by_tag_set(self, tag_set: set[str]):
        tag_objects = Tag.objects.in_tag_set(tag_set)

        self.obj.tags.remove(*tag_objects)

    def set_tags_from_tag_set(self, tag_set: set[str]):
        self._update_global_tags_from_set(tag_set)

        tag_objects = Tag.objects.in_tag_set(tag_set)
        self.obj.tags.set(tag_objects)

    @staticmethod
    def _update_global_tags_from_set(tag_set: set[str]):
        Tag.add_tags([Tag(name=tag) for tag in tag_set])
