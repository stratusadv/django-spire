from __future__ import annotations

from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.models import Visual
from django_spire.metric.visual.seeding.constants import VISUAL_SEEDS
from django_spire.metric.visual.seeding.seeder import VisualSeeder
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class VisualSeederTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group, name='Page Views')

    def test_seeds_curated_visuals(self) -> None:
        VisualSeeder(verbose=False).seed_database()

        seeds_by_name = {seed['name']: seed for seed in VISUAL_SEEDS}
        visuals = list(Visual.objects.all())

        assert len(visuals) == len(VISUAL_SEEDS)

        for visual in visuals:
            seed = seeds_by_name[visual.name]
            assert visual.kind == seed['kind']
            assert visual.statistic is not None
            assert visual.description == seed['description']
            assert visual.date == timezone.localdate()

    def test_seeded_visuals_display_data(self) -> None:
        VisualSeeder(verbose=False).seed_database()

        for visual in Visual.objects.all():
            if visual.kind == 'pie':
                assert len(visual.services.transformation.series_breakdown()) > 1
            else:
                assert visual.services.transformation.current_value() > 0
                assert len(visual.services.transformation.series_data()) >= 1
                assert len(visual.services.transformation.series_datasets()) >= 1
