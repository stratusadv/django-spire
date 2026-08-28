from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)


class PresentationPageViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()

    def test_list_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:presentation:page:list'))

        assert response.status_code == 200
        assert self.presentation in response.context_data['presentations']

    def test_detail_view(self):
        slide = create_test_slide(self.presentation)
        create_test_section(slide, row=1, col=1)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:page:detail',
                kwargs={'pk': self.presentation.pk},
            )
        )

        assert response.status_code == 200
        assert response.context_data['presentation'] == self.presentation
        assert len(response.context_data['slides']) == 1
        assert len(response.context_data['slides'][0]['sections']) == 1
        assert 'chart' in response.context_data['slides'][0]['sections'][0]
