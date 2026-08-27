from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import Seeder

from django_spire.metric.visual.models import Visual
from django_spire.metric.visual.presentation import models
from django_spire.metric.visual.presentation.seeding.constants import (
    PRESENTATION_SEEDS,
    SLIDE_SECTION_VISUALS,
    SLIDE_TITLES,
)

if TYPE_CHECKING:
    from typing import ClassVar

    from django.db.models import QuerySet

SLIDE_COUNT = 3


class PresentationSeeder(Seeder):
    model_class = models.Presentation

    fields_seeds: ClassVar = {}

    def seed_database(self, count: int | None = None) -> QuerySet:  # noqa: ARG002
        model_objects = []

        for presentation_index, seed in enumerate(PRESENTATION_SEEDS):
            presentation = models.Presentation.objects.create(
                name=seed['name'], description=seed['description'], is_active=True, is_deleted=False
            )
            self._seed_slides(presentation, presentation_index)
            model_objects.append(presentation)

        self._model_object_ids = [model_object.id for model_object in model_objects]

        return self.queryset

    @classmethod
    def _seed_slides(cls, presentation: models.Presentation, presentation_index: int) -> None:
        start = presentation_index % len(SLIDE_TITLES)

        for order in range(SLIDE_COUNT):
            slide_title = SLIDE_TITLES[(start + order) % len(SLIDE_TITLES)]
            slide = models.Slide.objects.create(
                presentation=presentation, name=slide_title, order=order
            )
            cls._seed_sections(slide)

    @staticmethod
    def _seed_sections(slide: models.Slide) -> None:
        visuals = list(Visual.objects.active())

        if not visuals:
            return

        visuals_by_name = {visual.name: visual for visual in visuals}
        visual_names = SLIDE_SECTION_VISUALS.get(slide.name) or [visual.name for visual in visuals]

        for order, visual_name in enumerate(visual_names):
            visual = visuals_by_name.get(visual_name) or visuals[order % len(visuals)]
            models.SlideSection.objects.create(slide=slide, visual=visual, row=order + 1, col=1)
