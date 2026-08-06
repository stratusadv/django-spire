from django.db.models.query import QuerySet

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.models import Domain
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup, StatisticValue


class StatisticGroupSeeder(Seeder):
    model_class = StatisticGroup

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'domain_id': Seeder.model.random_foreign_key(Domain),
        'name': Seeder.fake.company(),
        'description': Seeder.fake.paragraph(2),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class StatisticSeeder(Seeder):
    model_class = Statistic

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'group_id': Seeder.model.random_foreign_key(StatisticGroup),
        'name': Seeder.fake.word(),
        'interval': Seeder.model.random_field_choice(StatisticIntervalChoices),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }


class StatisticValueSeeder(Seeder):
    model_class = StatisticValue

    fields_seeds = {
        'id': Seeder.exclude(),
        'statistic_id': Seeder.model.random_foreign_key(Statistic),
        'reference': Seeder.random.choice(['/home/', '/dashboard/', '/contact/', '/pricing/']),
        'date': Seeder.fake.provider('date_between', start_date='-30d', end_date='now'),
        'value': Seeder.random.int(1, 100),
        'updated_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        model_objects = []

        for fields_values in self.to_list_of_dicts():
            statistic_value, _ = StatisticValue.objects.update_or_create(
                statistic_id=fields_values['statistic_id'],
                reference=fields_values['reference'],
                date=fields_values['date'],
                defaults={'value': fields_values['value']},
            )
            model_objects.append(statistic_value)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset
