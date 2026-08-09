from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.charts import VisualLineChart
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class PresentationTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()

    def test_slides_orders_and_excludes_deleted(self):
        slide_a = create_test_slide(self.presentation, name='A', order=1)
        create_test_slide(self.presentation, name='B', order=2)
        slide_c = create_test_slide(self.presentation, name='C', order=3)
        slide_c.set_deleted()

        slides = self.presentation.services.transformation.slides()

        assert list(slides) == [slide_a, self.presentation.slides.get(name='B')]

    def test_slide_count(self):
        create_test_slide(self.presentation)
        create_test_slide(self.presentation, order=1)

        assert self.presentation.services.transformation.slide_count() == 2


class SlideTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        self.slide = create_test_slide(self.presentation)

    def test_sections_orders_and_selects_visual(self):
        create_test_section(self.slide, row=2, col=1)
        section = create_test_section(self.slide, row=1, col=2)

        sections = list(self.slide.services.transformation.sections())

        assert sections[0] == section
        assert all(s.visual_id for s in sections)

    def test_sections_excludes_deleted(self):
        section = create_test_section(self.slide, row=1, col=1)
        section.set_deleted()

        assert self.slide.services.transformation.sections().count() == 0


class SlideSectionTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()
        self.slide = create_test_slide(self.presentation)

    def test_render_context_with_without_chart_kind(self):
        section = create_test_section(self.slide, row=1, col=1)

        context = section.services.transformation.render_context()

        assert context['visual'] == section.visual
        assert context['current_value'] is not None
        assert context['current_condition'] is not None
        assert context['chart'] is None

    def test_render_context_with_chart_kind(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)

        section = create_test_section(self.slide, row=1, col=1)
        section.visual = visual
        section.save()

        context = section.services.transformation.render_context()

        assert isinstance(context['chart'], VisualLineChart)

    def test_render_context_without_visual(self):
        section = create_test_section(self.slide, row=1, col=1, with_visual=False)

        context = section.services.transformation.render_context()

        assert context['visual'] is None
        assert context['current_value'] is None
        assert context['current_condition'] is None
        assert context['chart'] is None
