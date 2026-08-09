from __future__ import annotations

import random
from typing import TYPE_CHECKING

from django.db.models import QuerySet

from django_spire.contrib.seeding import Seeder

from django_spire.metric.visual.presentation.models import Presentation
from django_spire.metric.visual.signage import models

if TYPE_CHECKING:
    from typing import ClassVar


class SignageSeeder(Seeder):
    model_class = models.Signage

    fields_seeds: ClassVar = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.fake.sentence(),
        'description': Seeder.fake.paragraph(2),
        'key': Seeder.exclude(),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        model_objects = []

        for fields_values in self.to_list_of_dicts():
            signage = models.Signage.objects.create(**fields_values)
            self._seed_links(signage)
            model_objects.append(signage)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset

    def _seed_links(self, signage: models.Signage) -> None:
        presentation_ids = list(Presentation.objects.active().values_list('id', flat=True))

        if not presentation_ids:
            return

        for order, presentation_id in enumerate(
            random.sample(presentation_ids, min(3, len(presentation_ids)))
        ):
            models.SignagePresentation.objects.create(
                signage=signage, presentation_id=presentation_id, order=order
            )
