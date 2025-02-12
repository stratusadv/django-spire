from dandy.llm import Prompt
from django.test import TestCase

from django_spire.seeding.helper import SeedHelper
from django_spire.seeding.models import PersonSeedingModel


class SeedingTestCase(TestCase):
    def setUp(self):
        self.person_seed_helper = SeedHelper(
            model_class=PersonSeedingModel,
            seeding_prompt=(
                Prompt()
                .text('Create a bunch of unique people to be used for seeding.')
            ),
            count=5,
            exclude_fields=['phone_number'],
        )

    def tearDown(self):
        pass

    def test_seeding_helper_intel_class(self):
        person_intel_class = self.person_seed_helper.build_intel_class()
        
        print(person_intel_class.model_json_schema())
