from __future__ import annotations

from django.core.cache import cache

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)
from django_spire.metric.visual.signage.tests.factories import (
    create_test_link,
    create_test_signage,
    create_test_signage_links,
)


class SignageTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        cache.clear()

        self.signage = create_test_signage()

    def test_display_title_falls_back_to_name(self):
        assert self.signage.services.transformation.display_title == self.signage.name

    def test_display_title_uses_title_when_set(self):
        self.signage.title = 'Lobby Display'
        self.signage.save()

        assert self.signage.services.transformation.display_title == 'Lobby Display'

    def test_presentation_links_ordered(self):
        create_test_link(self.signage, order=2)
        create_test_link(self.signage, order=0)

        links = list(self.signage.services.transformation.presentation_links())

        assert [link.order for link in links] == [0, 2]

    def test_presentation_links_exclude_deleted(self):
        link = create_test_link(self.signage, order=0)
        link.set_deleted()

        assert self.signage.services.transformation.presentation_links().count() == 0

    def test_presentations_exclude_deleted_link(self):
        link = create_test_link(self.signage, order=0)
        link.set_deleted()

        assert self.signage.services.transformation.presentations().count() == 0

    def test_presentation_links_exclude_deleted_presentation(self):
        link = create_test_link(self.signage, order=0)
        link.presentation.set_deleted()

        assert self.signage.services.transformation.presentation_links().count() == 0
        assert self.signage.services.transformation.presentations().count() == 0

    def test_presentations_ordered(self):
        create_test_link(self.signage, order=1)
        create_test_link(self.signage, order=0)

        presentations = self.signage.services.transformation.presentations()

        assert list(presentations) != []

        presentations_by_pk = {presentation.pk: presentation for presentation in presentations}

        ordered_pks = [
            link.presentation_id
            for link in self.signage.services.transformation.presentation_links()
        ]

        assert [presentation.pk for presentation in presentations] == ordered_pks
        assert all(presentations_by_pk[pk].slides.all() is not None for pk in ordered_pks)

    def test_display_slides(self):
        create_test_signage_links(self.signage, count=2)

        slides = self.signage.services.transformation.display_slides()

        assert len(slides) == 2
        assert all('presentation' in slide and 'slide' in slide for slide in slides)
        assert all(slide['sections'][0]['visual'] is not None for slide in slides)
        assert all(
            slide['sections'][0]['grid_style'] == 'grid-column: 1 / span 12; grid-row: 2;'
            for slide in slides
        )

    def test_display_slides_query_count_does_not_scale_with_slides(self):
        presentation = create_test_presentation(name='multi_slide')
        for order in range(3):
            slide = create_test_slide(presentation, order=order)
            create_test_section(slide, row=1, col=1)

        create_test_link(self.signage, presentation=presentation, order=0)

        self.signage.services.transformation.display_slides()

        with self.assertNumQueries(10):
            slides = self.signage.services.transformation.display_slides()

        assert len(slides) == 3

    def test_display_slides_excludes_deleted_sections(self):
        presentation = create_test_presentation(name='mixed')
        slide = create_test_slide(presentation, order=0)
        section = create_test_section(slide, row=1, col=1)
        create_test_section(slide, row=1, col=2, with_visual=False)

        section.visual.set_deleted()
        create_test_link(self.signage, presentation=presentation, order=0)

        slides = self.signage.services.transformation.display_slides()

        assert slides[0]['sections'] == []
