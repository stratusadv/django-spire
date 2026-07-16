from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.tests.test_seeder import TaskSeeder

from test_project.app.task.choices import TaskStatusChoices
from test_project.app.task.models import Task


class TestSeederIntegration(TestCase):
    def test_all_fields_populated(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert 'name' in seed.to_dict()
            assert 'status' in seed.to_dict()
            assert 'description' in seed.to_dict()
            assert 'created_datetime' in seed.to_dict()
            assert 'is_active' in seed.to_dict()
            assert 'is_deleted' in seed.to_dict()

    def test_seed_database_persists_to_db(self):
        initial_count = Task.objects.count()
        seeder = TaskSeeder(count=3, verbose=False)
        seeder.seed_database()
        assert Task.objects.count() == initial_count + 3

    def test_queryset_returns_exact_objects(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed_database()
        qs = seeder.queryset
        assert qs.count() == 2
        for obj in qs:
            assert isinstance(obj, Task)
            assert obj.name != ''
            assert obj.status in [choice[0] for choice in TaskStatusChoices.choices]

    def test_llm_fields_filled_by_bot(self):
        seeder = TaskSeeder(count=1, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert seed['description'] is not None
            assert isinstance(seed['description'], str)
            assert len(seed['description']) > 0

    def test_post_seed_hook_modifies_seeds(self):
        class ModifiedSeeder(TaskSeeder):
            def __post_seed__(self) -> None:
                for seed in self.seeds:
                    seed['name'] = 'Modified Name'

        seeder = ModifiedSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert seed['name'] == 'Modified Name'

    def test_faker_provider_deterministic(self):
        seeder = TaskSeeder(count=3, verbose=False)
        seeder.seed()
        first_run_names = [seed['name'] for seed in seeder.seeds]
        seeder.reseed(count=3)
        second_run_names = [seed['name'] for seed in seeder.seeds]
        assert first_run_names == second_run_names

    def test_only_llm_fields_filled(self):
        class LlmOnlySeeder(Seeder):
            model_class = Task
            cache_enabled = False
            fields_seeds = {
                'id': Seeder.exclude(),
                'parent_id': Seeder.exclude(),
                'name': Seeder.llm(str, 'A creative task name'),
                'status': Seeder.llm(str),
                'description': Seeder.llm(str),
                'created_datetime': Seeder.exclude(),
                'is_active': Seeder.exclude(),
                'is_deleted': Seeder.exclude(),
            }

        seeder = LlmOnlySeeder(count=1, verbose=False)
        seeder.seed()
        seed = seeder.seeds[0]
        assert seed['name'] is not None
        assert seed['status'] is not None
        assert seed['description'] is not None
