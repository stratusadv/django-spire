from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.models import Presentation
from django_spire.metric.visual.presentation.seeding.constants import PRESENTATION_SEEDS
from django_spire.metric.visual.presentation.seeding.seeder import PresentationSeeder
from django_spire.metric.visual.signage.models import Signage, SignagePresentation
from django_spire.metric.visual.signage.seeding.constants import (
    SIGNAGE_PRESENTATION_LINKS,
    SIGNAGE_SEEDS,
)
from django_spire.metric.visual.signage.seeding.seeder import SignageSeeder
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class SignageSeederTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)

        for order in range(3):
            create_test_visual(
                statistic=statistic, name=f'visual {order}', kind='line', with_conditions=False
            )

        PresentationSeeder(count=len(PRESENTATION_SEEDS), verbose=False).seed_database()

    def test_seeds_curated_signages(self) -> None:
        SignageSeeder(count=len(SIGNAGE_SEEDS), verbose=False).seed_database()

        signages = list(Signage.objects.order_by('pk'))

        assert len(signages) == len(SIGNAGE_SEEDS)
        assert [signage.name for signage in signages] == [seed['name'] for seed in SIGNAGE_SEEDS]
        assert [str(signage.key) for signage in signages] == [seed['key'] for seed in SIGNAGE_SEEDS]

    def test_seeds_slide_display_seconds(self) -> None:
        SignageSeeder(count=len(SIGNAGE_SEEDS), verbose=False).seed_database()

        signages = list(Signage.objects.order_by('pk'))

        assert [signage.slide_display_seconds for signage in signages] == [
            seed['slide_display_seconds'] for seed in SIGNAGE_SEEDS
        ]
        assert all(10 <= signage.slide_display_seconds <= 60 for signage in signages)

    def test_seeds_display_title(self) -> None:
        SignageSeeder(count=len(SIGNAGE_SEEDS), verbose=False).seed_database()

        signages = list(Signage.objects.order_by('pk'))

        assert [signage.title for signage in signages] == [seed['title'] for seed in SIGNAGE_SEEDS]

    def test_seeded_links_flow_from_presentations(self) -> None:
        SignageSeeder(count=len(SIGNAGE_SEEDS), verbose=False).seed_database()

        for signage in Signage.objects.all():
            presentation_names = SIGNAGE_PRESENTATION_LINKS[signage.name]
            links = list(
                signage.signage_presentations.select_related('presentation').order_by('order')
            )

            assert len(links) == len(presentation_names)
            assert [link.presentation.name for link in links] == presentation_names
            assert [link.order for link in links] == list(range(len(presentation_names)))

    def test_seeded_links_skip_without_presentations(self) -> None:
        Presentation.objects.all().delete()
        SignageSeeder(count=len(SIGNAGE_SEEDS), verbose=False).seed_database()

        assert SignagePresentation.objects.count() == 0
