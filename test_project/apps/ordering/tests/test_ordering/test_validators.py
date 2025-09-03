from django_spire.core.tests.test_cases import BaseTestCase
from test_project.apps.ordering.models import Duck
from test_project.apps.ordering.tests.test_ordering.factories import create_test_duck

class TestOrderingMixinValidator(BaseTestCase):
    def setUp(self):
        self.test_duck = create_test_duck()
        self.test_other_duck = create_test_duck(name='Duckworth IV', order=1)
        super().setUp()

    def test_invalid_position(self):
        all_ducks = Duck.objects.all()

        with self.assertRaises(ExceptionGroup):
            self.test_duck.ordering_services.processor.move_to_position(
                destination_objects=all_ducks,
                position=49,
                origin_objects=all_ducks,
            )

    def test_valid_position(self):
        all_ducks = Duck.objects.all()

        self.test_duck.ordering_services.processor.move_to_position(
            destination_objects=all_ducks,
            position=1,
            origin_objects=all_ducks,
        )