from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.models import Presentation
from django_spire.metric.visual.presentation.seeding.constants import (
    PRESENTATION_SEEDS,
    SLIDE_SECTION_VISUALS,
    SLIDE_TITLES,
)
from django_spire.metric.visual.presentation.seeding.seeder import PresentationSeeder
from django_spire.metric.visual.seeding.seeder import VisualSeeder
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class PresentationSeederTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)

        for order in range(3):
            create_test_visual(
                statistic=statistic, name=f'visual {order}', kind='line', with_conditions=False
            )

    def test_seeds_curated_presentations(self) -> None:
        PresentationSeeder(verbose=False).seed_database()

        presentations = list(Presentation.objects.order_by('pk'))

        assert len(presentations) == len(PRESENTATION_SEEDS)
        assert [presentation.name for presentation in presentations] == [
            seed['name'] for seed in PRESENTATION_SEEDS
        ]
        assert all(
            slide.name in SLIDE_TITLES
            for presentation in presentations
            for slide in presentation.slides.all()
        )

    def test_seeded_sections_flow_from_visuals(self) -> None:
        PresentationSeeder(verbose=False).seed_database()

        for presentation in Presentation.objects.all():
            for slide in presentation.slides.order_by('order'):
                sections = list(slide.sections.select_related('visual').order_by('row', 'col'))

                assert len(sections) == len(SLIDE_SECTION_VISUALS[slide.name])
                assert [section.row for section in sections] == [
                    index // 2 for index in range(len(sections))
                ]
                assert [section.col for section in sections] == [
                    index % 2 for index in range(len(sections))
                ]
                assert all(section.visual_id for section in sections)

                for section in sections:
                    context = section.services.transformation.render_context()

                    assert context['visual'] is not None
                    assert context['current_value'] is not None or context['chart'] is not None

    def test_seeded_sections_use_curated_visuals(self) -> None:
        VisualSeeder(verbose=False).seed_database()
        PresentationSeeder(verbose=False).seed_database()

        for presentation in Presentation.objects.all():
            for slide in presentation.slides.all():
                visual_names = SLIDE_SECTION_VISUALS[slide.name]

                assert [section.visual.name for section in slide.sections.all()] == visual_names
