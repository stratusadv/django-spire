from django.db import models
from django.test import TestCase

from django_spire.core.tags.mixins import TagsModelMixin
from django_spire.core.tags.models import Tag
from django_spire.knowledge.collection.models import Collection


class TestTags(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(
            name='Test Collection',
            description='Test Collection Description'
        )

        self.new_tags = {'apple', 'banana', 'orange'}
        self.messy_tags = {'HaT', 'four tacos', '123 hoop'}

    def test_tag_model(self):
        self.collection.add_tag_set(self.new_tags)

        self.assertEqual(Tag.objects.count(), 3)

        self.collection.add_tag_set(self.messy_tags)

        self.assertEqual(Tag.objects.count(), 6)

        self.collection.add_tag_set(self.new_tags)

        self.assertEqual(Tag.objects.count(), 6)
