from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.signage.tests.factories import (
    create_test_link,
    create_test_signage,
    create_test_signage_links,
)


class SignageTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.signage = create_test_signage()

    def test_presentation_links_ordered(self):
        create_test_link(self.signage, order=2)
        create_test_link(self.signage, order=0)

        links = list(self.signage.services.transformation.presentation_links())

        assert [link.order for link in links] == [0, 2]

    def test_presentation_links_exclude_deleted(self):
        link = create_test_link(self.signage, order=0)
        link.set_deleted()

        assert self.signage.services.transformation.presentation_links().count() == 0

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
