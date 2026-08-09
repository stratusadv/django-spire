from __future__ import annotations

import random
from typing import TYPE_CHECKING

from django.db.models import QuerySet

from django_spire.contrib.seeding import Seeder

from django_spire.metric.visual.models import Visual
from django_spire.metric.visual.presentation import models

if TYPE_CHECKING:
    from typing import ClassVar


class PresentationSeeder(Seeder):
    model_class = models.Presentation

    fields_seeds: ClassVar = {
        'id': Seeder.exclude(),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'name': Seeder.fake.sentence(),
        'description': Seeder.fake.paragraph(2),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def seed_database(self, count: int | None = None) -> QuerySet:
        self.seed(count)

        model_objects = []

        for fields_values in self.to_list_of_dicts():
            presentation = models.Presentation.objects.create(**fields_values)
            self._seed_slides(presentation)
            model_objects.append(presentation)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset

    def _seed_slides(self, presentation: models.Presentation) -> None:
        for order in range(random.randint(1, 3)):
            slide = models.Slide.objects.create(
                presentation=presentation,
                name=Seeder.fake.sentence(nb_words=4).generate_value(0),
                order=order,
            )
            self._seed_sections(slide)

    def _seed_sections(self, slide: models.Slide) -> None:
        visual_ids = list(Visual.objects.active().values_list('id', flat=True))

        if not visual_ids:
            return

        for _ in range(random.randint(2, 4)):
            models.SlideSection.objects.create(
                slide=slide,
                visual_id=random.choice(visual_ids),
                row=random.randint(1, 2),
                col=random.randint(1, 12),
            )
