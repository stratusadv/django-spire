from django.test import TestCase

from django_spire.core.tags.models import Tag
from django_spire.knowledge.collection.models import Collection


class TestTags(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(
            name='Test Collection',
            description='Test Collection Description'
        )

        self.tag_set_a = {'apple', 'banana', 'orange'}
        self.tag_set_b = {'grape', 'kiwi', 'pear'}
        self.tag_set_c = {'lemon', 'lime', 'mango'}
        self.mixed_tag_set = {'apple', 'grape', 'lemon'}
        self.bad_tag_set = {'HaT~', 'four* tacos', '123 hoop!!'}

    def test_tag_model(self):
        self.collection.add_tag_set(self.tag_set_a)
        self.collection.add_tag_set(self.tag_set_b)
        self.collection.add_tag_set(self.tag_set_c)
        self.collection.add_tag_set(self.mixed_tag_set)
        self.collection.add_tag_set(self.bad_tag_set)

        print(Tag.objects.all())
        self.assertEqual(Tag.objects.count(), 12)
        print(self.collection.tags.all())
        self.assertEqual(self.collection.tags.count(), 12)
        self.assertEqual(self.collection.aggregated_tags.count(), 12)

        self.collection.remove_tag_set(self.tag_set_a)

        self.assertEqual(Tag.objects.count(), 9)

