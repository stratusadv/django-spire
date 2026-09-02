from __future__ import annotations

from django_spire.contrib.seeding import Seeder

from django_spire.metric.visual.models import Visual
from django_spire.metric.visual.presentation import models
from django_spire.metric.visual.presentation.seeding.constants import (
    PRESENTATION_SEEDS,
    SLIDE_SECTION_VISUALS,
    SLIDE_TITLES,
)

SLIDE_COUNT = 3


class PresentationSeeder(Seeder):
    cache_enabled = False
    model_class = models.Presentation

    fields_seeds = {
        'id': Seeder.exclude(),
        'name': Seeder.ordered.choice([seed['name'] for seed in PRESENTATION_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in PRESENTATION_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def __post_seed_database__(self) -> None:
        for index, presentation in enumerate(self.queryset.order_by('pk')):
            self._seed_slides(presentation, index)

    @classmethod
    def _seed_slides(cls, presentation: models.Presentation, presentation_index: int) -> None:
        start = presentation_index % len(SLIDE_TITLES)

        for order in range(SLIDE_COUNT):
            slide_title = SLIDE_TITLES[(start + order) % len(SLIDE_TITLES)]
            slide = models.Slide.objects.create(
                presentation=presentation,
                name=slide_title,
                order=order,
                is_active=True,
                is_deleted=False,
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
            models.SlideSection.objects.create(
                slide=slide,
                row=order // 2,
                col=order % 2,
                visual=visual,
                is_active=True,
                is_deleted=False,
            )
