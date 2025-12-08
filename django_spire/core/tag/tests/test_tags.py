from __future__ import annotations

from django.test import TestCase

from django_spire.core.tag.models import Tag
from django_spire.knowledge.collection.models import Collection


class TestTags(TestCase):
    def setUp(self) -> None:
        self.collection = Collection.objects.create(
            name='Test Collection',
            description='Test Collection Description'
        )

        self.tag_set_a = {'apple', 'banana', 'orange'}
        self.tag_set_b = {'grape', 'kiwi', 'pear'}
        self.tag_set_c = {'lemon', 'lime', 'mango'}

        self.mixed_tag_set = {'apple', 'grape', 'lemon'}

        self.dirty_tag_set = {'HaT~', 'four* tacos', '123 hoop!!'}

        self.collection.services.tag.add_tags_from_tag_set(self.tag_set_a)
        self.collection.services.tag.add_tags_from_tag_set(self.tag_set_b)
        self.collection.services.tag.add_tags_from_tag_set(self.tag_set_c)

        self.collection.services.tag.add_tags_from_tag_set(self.mixed_tag_set)

        self.collection.services.tag.add_tags_from_tag_set(self.dirty_tag_set)

    def test_tag_add_and_set(self) -> None:
        self.collection.services.tag.set_tags_from_tag_set(self.mixed_tag_set)

        assert 'lemon' in self.collection.tag_set
        assert 'banana' not in self.collection.tag_set

    def test_tag_bool_methods(self) -> None:
        self.collection.services.tag.remove_tags_by_tag_set(self.tag_set_b)

        assert self.collection.services.tag.has_tags_in_tag_set(self.tag_set_c) is True
        assert self.collection.services.tag.has_tags_in_tag_set(self.mixed_tag_set) is False

    def test_tag_count(self) -> None:
        assert Tag.objects.count() == 12
        assert self.collection.tags.count() == 12

    def test_tag_matching_methods(self) -> None:
        assert len(self.collection.services.tag.get_matching_tags_from_tag_set(self.tag_set_a)) == 3

        self.collection.services.tag.remove_tags_by_tag_set(self.tag_set_a)

        assert len(self.collection.services.tag.get_matching_tags_from_tag_set(self.tag_set_a)) == 0
        assert len(self.collection.services.tag.get_matching_tags_from_tag_set(self.tag_set_b)) == 3
        assert len(self.collection.services.tag.get_matching_tags_from_tag_set(self.mixed_tag_set)) == 2

        self.collection.services.tag.remove_tags_by_tag_set(self.tag_set_b)

        assert len(self.collection.services.tag.get_matching_tags_from_tag_set(self.tag_set_b)) == 0
        assert len(self.collection.services.tag.get_matching_tags_from_tag_set(self.mixed_tag_set)) == 1

    def test_tag_metric_methods(self) -> None:
        assert abs(
            self.collection.services.tag.get_matching_percentage_of_tag_set(self.tag_set_a) - 1.00
        ) < 0.01

        assert abs(
            self.collection.services.tag.get_matching_percentage_of_model_tags_from_tag_set(self.tag_set_b) - 0.25
        ) < 0.01

        self.collection.services.tag.remove_tags_by_tag_set(self.mixed_tag_set)

        assert abs(
            self.collection.services.tag.get_matching_percentage_of_tag_set(self.tag_set_a) - 0.666
        ) < 0.01

        assert abs(
            self.collection.services.tag.get_matching_percentage_of_model_tags_from_tag_set(self.tag_set_b) - 0.222
        ) < 0.01

    def test_tag_removal(self) -> None:
        assert 'apple' in self.collection.tag_set

        self.collection.services.tag.remove_tags_by_tag_set(self.mixed_tag_set)

        assert 'lemon' not in self.collection.tag_set
        assert 'kiwi' in self.collection.tag_set

    def test_tag_removal_count(self) -> None:
        self.collection.services.tag.remove_tags_by_tag_set(self.tag_set_a)

        assert self.collection.tags.count() == 9
