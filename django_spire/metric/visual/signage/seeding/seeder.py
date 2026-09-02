from __future__ import annotations

from django_spire.contrib.seeding import Seeder

from django_spire.metric.visual.presentation.models import Presentation
from django_spire.metric.visual.signage import models
from django_spire.metric.visual.signage.seeding.constants import (
    SIGNAGE_PRESENTATION_LINKS,
    SIGNAGE_SEEDS,
)


class SignageSeeder(Seeder):
    cache_enabled = False
    model_class = models.Signage

    fields_seeds = {
        'id': Seeder.exclude(),
        'key': Seeder.ordered.choice([seed['key'] for seed in SIGNAGE_SEEDS], wrap=True),
        'name': Seeder.ordered.choice([seed['name'] for seed in SIGNAGE_SEEDS], wrap=True),
        'title': Seeder.ordered.choice([seed['title'] for seed in SIGNAGE_SEEDS], wrap=True),
        'description': Seeder.ordered.choice(
            [seed['description'] for seed in SIGNAGE_SEEDS], wrap=True
        ),
        'slide_display_seconds': Seeder.ordered.choice(
            [seed['slide_display_seconds'] for seed in SIGNAGE_SEEDS], wrap=True
        ),
        'is_active': Seeder.static(True),
        'is_deleted': Seeder.static(False),
    }

    def __post_seed_database__(self) -> None:
        for signage in self.queryset:
            self._seed_links(signage)

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
                signage=signage,
                order=order,
                presentation=presentation,
                is_active=True,
                is_deleted=False,
            )
