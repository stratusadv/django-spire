from __future__ import annotations

from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.models import Visual, VisualRegion
from django_spire.metric.visual.seeding.constants import VISUAL_REGION_SEEDS, VISUAL_SEEDS
from django_spire.metric.visual.seeding.seeder import VisualRegionSeeder, VisualSeeder
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


class VisualRegionSeederTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group, name='Page Views')

        VisualSeeder(verbose=False).seed_database()

    def test_seeds_assigned_regions(self) -> None:
        VisualRegionSeeder(verbose=False).seed_database()

        seeds_by_key = {seed['key']: seed for seed in VISUAL_REGION_SEEDS}
        regions = list(VisualRegion.objects.all())

        assert len(regions) == len(VISUAL_REGION_SEEDS)

        for region in regions:
            seed = seeds_by_key[region.key]
            assert region.visual.name == seed['visual_name']
            assert region.title == seed['title']
            assert region.is_live_updated is seed['is_live_updated']

    def test_seed_is_idempotent(self) -> None:
        VisualRegionSeeder(verbose=False).seed_database()
        VisualRegionSeeder(verbose=False).seed_database()

        assert VisualRegion.objects.count() == len(VISUAL_REGION_SEEDS)
        assert all(region.visual is not None for region in VisualRegion.objects.all())
