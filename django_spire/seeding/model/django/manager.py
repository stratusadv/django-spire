from django.db.models.base import Model

from django_spire.seeding.callable_seeder import CallableSeeder
from django_spire.seeding.custom_seeder import CustomSeeder
from django_spire.seeding.django_model.seeder import BaseDjangoModelSeeder, DjangoModelLlmSeeder, DjangoModelFakerSeeder
from django_spire.seeding.static_seeder import StaticSeeder

from dandy.llm import Prompt


class DjangoModelSeederManager(BaseDjangoModelSeeder):
    prompt: Prompt = None

    _seeders = [
        CustomSeeder,
        CallableSeeder,
        StaticSeeder,
        DjangoModelLlmSeeder,
        DjangoModelFakerSeeder
    ]

    # @classmethod
    # def _llm_seed_data(cls, count=1) -> list[dict]:


    #     return DjangoModelLlmSeeder(
    #         cls.model_class,
    #         self.filter_fields('llm'),
    #         count
    #     ).generate_data(self.prompt, self.cache_buster)


    @classmethod
    def seed_data(
            cls,
            count=1,
            fields: dict | None = None
    ) -> list[dict]:
        original_fields = cls.fields.copy()

        if fields:
            cls._normalize_fields(fields)

        seed_data = []

        # Todo: LLM Seeder Takes a prompt
        for seeder_cls in cls._seeders:
            seeder = seeder_cls(cls.fields, cls.default_to)

            seed_data.extend(seeder.seed(cls, count))


        # Todo: need to combine all the seed data into a list of single dict.
        #  The list should be of length count.

        # Todo: Pass seed manager to seeder. Model Instance. Model & Field Seeders

        cls.fields = original_fields
        return seed_data

    @classmethod
    def seed(
            cls,
            count: int = 1,
            fields: dict | None = None,
    ) -> list[Model]:
        return [
            cls.model_class(**seed_data)
            for seed_data in cls.seed_data(count, fields)
        ]

    def seed_database(
            self,
            count: int = 1,
            fields: dict | None = None,
    ):
        model_objects = self.seed(count, fields)
        return self.model_class.objects.bulk_create(model_objects)
