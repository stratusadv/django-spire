from django.test import TestCase

from django_spire.core.tags.models import Tag
from django_spire.knowledge.collection.models import Collection


class TestTags(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(
            name='Test Collection', description='Test Collection Description'
        )

        self.tag_set_a = {'apple', 'banana', 'orange'}
        self.tag_set_b = {'grape', 'kiwi', 'pear'}
        self.tag_set_c = {'lemon', 'lime', 'mango'}

        self.mixed_tag_set = {'apple', 'grape', 'lemon'}

        self.dirty_tag_set = {'HaT~', 'four* tacos', '123 hoop!!'}

        self.collection.add_tag_set(self.tag_set_a)
        self.collection.add_tag_set(self.tag_set_b)
        self.collection.add_tag_set(self.tag_set_c)

        self.collection.add_tag_set(self.mixed_tag_set)

        self.collection.add_tag_set(self.dirty_tag_set)

    def test_tag_set(self):
        self.assertIn('apple', self.collection.tag_set)
        self.assertIn('grape', self.collection.aggregated_tag_set)

        self.collection.remove_tag_set(self.mixed_tag_set)

        self.assertNotIn('lemon', self.collection.tag_set)
        self.assertIn('lemon', self.collection.aggregated_tag_set)

        self.collection.remove_tag_set_from_aggregated({'kiwi'})

        self.assertIn('kiwi', self.collection.tag_set)
        self.assertNotIn('kiwi', self.collection.aggregated_tag_set)

    def test_tag_count(self):
        self.assertEqual(Tag.objects.count(), 12)
        self.assertEqual(self.collection.tags.count(), 12)
        self.assertEqual(self.collection.aggregated_tags.count(), 12)

    def test_tag_removal(self):
        self.collection.remove_tag_set(self.tag_set_a)

        self.assertEqual(self.collection.tags.count(), 9)
        self.assertEqual(self.collection.aggregated_tags.count(), 12)

        self.collection.remove_tag_set_from_aggregated(self.tag_set_b)

        self.assertEqual(self.collection.tags.count(), 9)
        self.assertEqual(self.collection.aggregated_tags.count(), 9)

    def test_tag_bool_methods(self):
        self.collection.remove_tag_set(self.tag_set_b, remove_from_aggregated=True)

        self.assertTrue(self.collection.has_tag_set(self.tag_set_c))
        self.assertFalse(self.collection.has_tag_set(self.mixed_tag_set))

        self.assertTrue(self.collection.has_tag_set_in_aggregated(self.tag_set_a))
        self.assertFalse(self.collection.has_tag_set_in_aggregated(self.mixed_tag_set))

        self.assertFalse(
            self.collection.has_tag_set_in_aggregated({'a crazy tag that does not exist'})
        )

    def test_tag_matching_methods(self):
        self.assertEqual(len(self.collection.get_matching_tags_from_tag_set(self.tag_set_a)), 3)

        self.collection.remove_tag_set(self.tag_set_a)

        self.assertEqual(len(self.collection.get_matching_tags_from_tag_set(self.tag_set_a)), 0)
        self.assertEqual(len(self.collection.get_matching_tags_from_tag_set(self.tag_set_b)), 3)
        self.assertEqual(len(self.collection.get_matching_tags_from_tag_set(self.mixed_tag_set)), 2)

        self.collection.remove_tag_set(self.tag_set_b, remove_from_aggregated=True)

        self.assertEqual(len(self.collection.get_matching_tags_from_tag_set(self.tag_set_b)), 0)
        self.assertEqual(
            len(self.collection.get_matching_tags_in_aggregated_from_tag_set(self.tag_set_b)), 0
        )
        self.assertEqual(
            len(self.collection.get_matching_tags_in_aggregated_from_tag_set(self.mixed_tag_set)), 2
        )
        self.assertEqual(len(self.collection.get_matching_tags_from_tag_set(self.mixed_tag_set)), 1)

    def test_tag_metric_methods(self):
        self.assertAlmostEqual(
            self.collection.get_matching_tags_percentage_from_tag_set(self.tag_set_a),
            1.00,
            2
        )
        self.assertAlmostEqual(
            self.collection.get_matching_tags_in_aggregated_percentage_from_tag_set(self.tag_set_a),
            1.00,
            2,
        )

        self.assertAlmostEqual(
            self.collection.get_matching_model_tags_percentage_from_tag_set(self.tag_set_b),
            0.25,
            2
        )
        self.assertAlmostEqual(
            self.collection.get_matching_model_tags_in_aggregated_percentage_from_tag_set(
                self.tag_set_b
            ),
            0.25,
            2,
        )

        self.collection.remove_tag_set(self.mixed_tag_set, remove_from_aggregated=True)

        self.assertAlmostEqual(
            self.collection.get_matching_tags_percentage_from_tag_set(self.tag_set_a),
            0.666,
            2
        )
        self.assertAlmostEqual(
            self.collection.get_matching_tags_in_aggregated_percentage_from_tag_set(self.tag_set_a),
            0.666,
            2,
        )

        self.assertAlmostEqual(
            self.collection.get_matching_model_tags_percentage_from_tag_set(self.tag_set_b),
            0.222,
            2
        )
        self.assertAlmostEqual(
            self.collection.get_matching_model_tags_in_aggregated_percentage_from_tag_set(
                self.tag_set_b
            ),
            0.222,
            2,
        )
