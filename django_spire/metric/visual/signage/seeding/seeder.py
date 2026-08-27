from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import Seeder

from django_spire.metric.visual.presentation.models import Presentation
from django_spire.metric.visual.signage import models
from django_spire.metric.visual.signage.seeding.constants import (
    SIGNAGE_PRESENTATION_LINKS,
    SIGNAGE_SEEDS,
)

if TYPE_CHECKING:
    from typing import ClassVar

    from django.db.models import QuerySet


class SignageSeeder(Seeder):
    model_class = models.Signage

    fields_seeds: ClassVar = {}

    def seed_database(self, count: int | None = None) -> QuerySet:  # noqa: ARG002
        model_objects = []

        for seed in SIGNAGE_SEEDS:
            signage = models.Signage.objects.create(
                name=seed['name'],
                description=seed['description'],
                key=seed['key'],
                is_active=True,
                is_deleted=False,
            )
            self._seed_links(signage)
            model_objects.append(signage)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset

    @staticmethod
    def _seed_links(signage: models.Signage) -> None:
        presentations = list(Presentation.objects.active())

        if not presentations:
            return

        presentations_by_name = {presentation.name: presentation for presentation in presentations}
        presentation_names = SIGNAGE_PRESENTATION_LINKS.get(
            signage.name, [presentation.name for presentation in presentations]
        )

        for order, presentation_name in enumerate(presentation_names):
            presentation = (
                presentations_by_name.get(presentation_name)
                or presentations[order % len(presentations)]
            )
            models.SignagePresentation.objects.create(
                signage=signage, presentation=presentation, order=order
            )
