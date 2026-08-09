from __future__ import annotations

from decimal import Decimal

from django.db.models import QuerySet

from django_spire.contrib.seeding import Seeder
from django_spire.metric.domain.statistic.models import Statistic
from django_spire.metric.visual import models
from django_spire.metric.visual.choices import VisualKindChoices


class VisualSeeder(Seeder):
    model_class = models.Visual

    fields_seeds = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'statistic_id': Seeder.model.random_foreign_key(Statistic),
        'name': Seeder.fake.sentence(),
        'description': Seeder.fake.paragraph(2),
        'reference': Seeder.random.choice(['', '/home/', '/dashboard/', '/pricing/']),
        'kind': Seeder.model.random_field_choice(VisualKindChoices),
        'date': Seeder.fake.provider('date_this_month'),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        model_objects = []

        for fields_values in self.to_list_of_dicts():
            visual = models.Visual.objects.create(**fields_values)

            visual.services.factory.create_default_conditions(
                target=Decimal(100), tolerance=Decimal(10)
            )

            model_objects.append(visual)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset
