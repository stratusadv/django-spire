from django_spire.core.tests.test_cases import BaseTestCase
from test_project.apps.ordering.models import Duck
from test_project.apps.ordering.tests.test_ordering.factories import create_test_duck

class TestOrderingProcessorService(BaseTestCase):
    def setUp(self):
        self.test_duck = create_test_duck()
        self.test_other_duck = create_test_duck(name='Duckworth IV', order=1)
        super().setUp()

    def test_reorder_existing(self):
        all_ducks = Duck.objects.all()
        self.test_duck.ordering_services.processor.move_to_position(
            destination_objects=all_ducks,
            position=1,
        )

        self.test_duck.refresh_from_db()
        self.test_other_duck.refresh_from_db()

        self.assertEqual(self.test_duck.order, 1)
        self.assertEqual(self.test_other_duck.order, 0)

    def test_reorder_different_object_lists(self):
        all_ducks = Duck.objects.all()
        some_ducks = all_ducks.filter(name=self.test_duck.name)
        other_ducks = all_ducks.filter(name=self.test_other_duck.name)

        self.test_duck.ordering_services.processor.move_to_position(
            destination_objects=some_ducks,
            position=1,
            origin_objects=other_ducks,
        )

        self.test_duck.refresh_from_db()
        self.test_other_duck.refresh_from_db()

        self.assertEqual(self.test_duck.order, 1)
        self.assertEqual(self.test_other_duck.order, 0)

    def test_reorder_insert_new(self):
        new_duck = create_test_duck(name='Quackers', order=0)
        all_ducks = Duck.objects.all()
        self.test_duck.order = 0
        self.test_duck.save()
        self.test_other_duck.order = 1
        self.test_other_duck.save()
        new_duck.ordering_services.processor.move_to_position(
            destination_objects=all_ducks,
            position=1,
        )

        self.test_duck.refresh_from_db()
        self.test_other_duck.refresh_from_db()

        self.assertEqual(self.test_duck.order, 0)
        self.assertEqual(new_duck.order, 1)
        self.assertEqual(self.test_other_duck.order, 2)

    def test_remove_from_objects(self):
        all_ducks = Duck.objects.all()
        self.test_duck.order = 0
        self.test_duck.save()
        self.test_other_duck.order = 1
        self.test_other_duck.save()
        self.test_duck.ordering_services.processor.remove_from_objects(
            destination_objects=all_ducks
        )

        self.test_duck.refresh_from_db()
        self.test_other_duck.refresh_from_db()

        self.assertEqual(self.test_duck.order, 0)
        self.assertEqual(self.test_other_duck.order, 0)