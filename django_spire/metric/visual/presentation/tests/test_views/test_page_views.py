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
        section = create_test_section(slide, row=1, col=1)

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

        section_data = response.context_data['slides'][0]['sections'][0]
        assert 'chart' in section_data
        assert 'grid_style' in section_data

        content = response.content.decode()
        assert 'Row 1, Col 1' in content

        edit_url = reverse(
            'django_spire:metric:visual:presentation:form:update_section', kwargs={'pk': section.pk}
        )
        delete_url = reverse(
            'django_spire:metric:visual:presentation:form:delete_section', kwargs={'pk': section.pk}
        )
        assert edit_url in content
        assert delete_url in content

    def test_detail_view_empty_section_shows_placeholder(self):
        slide = create_test_slide(self.presentation)
        create_test_section(slide, row=0, col=0, with_visual=False)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:page:detail',
                kwargs={'pk': self.presentation.pk},
            )
        )

        content = response.content.decode()
        assert 'Row 0, Col 0' in content
        assert 'Empty' in content
