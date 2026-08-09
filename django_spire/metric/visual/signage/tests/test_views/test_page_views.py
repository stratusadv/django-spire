from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.signage.tests.factories import (
    create_test_signage,
    create_test_signage_links,
)


class SignagePageViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.signage = create_test_signage()

    def test_list_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:signage:page:list'))

        assert response.status_code == 200
        assert self.signage in response.context_data['signages']

    def test_detail_view(self):
        create_test_signage_links(self.signage, count=1)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:page:detail', kwargs={'pk': self.signage.pk}
            )
        )

        assert response.status_code == 200
        assert response.context_data['signage'] == self.signage
        assert len(response.context_data['presentation_links']) == 1

    def test_display_view(self):
        create_test_signage_links(self.signage, count=2)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:page:display', kwargs={'key': self.signage.key}
            )
        )

        assert response.status_code == 200
        assert response.context_data['signage'] == self.signage
        assert response.context_data['slide_count'] == 2
