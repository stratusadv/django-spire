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

    def test_detail_view_shows_display_title(self):
        self.signage.title = 'Lobby Display'
        self.signage.save()

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:page:detail', kwargs={'pk': self.signage.pk}
            )
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'Lobby Display' in content
        assert 'test_signage' in content

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
        assert response.context_data['slide_timer_seconds'] == 30
        content = response.content.decode()
        assert self.signage.name in content
        assert 'grid-auto-rows: minmax(0, 1fr)' in content
        assert 'height: 900px' in content
        assert 'container-type: size' in content
        assert '60cqh' in content

    def test_display_view_uses_display_title(self):
        self.signage.title = 'Lobby Display'
        self.signage.save()
        create_test_signage_links(self.signage, count=1)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:page:display', kwargs={'key': self.signage.key}
            )
        )

        assert response.status_code == 200
        assert 'Lobby Display' in response.content.decode()

    def test_display_view_uses_signage_slide_timer(self):
        self.signage.slide_display_seconds = 45
        self.signage.save()
        create_test_signage_links(self.signage, count=2)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:page:display', kwargs={'key': self.signage.key}
            )
        )

        assert response.status_code == 200
        assert response.context_data['slide_timer_seconds'] == 45
        assert 'delay: 45 * 1000' in response.content.decode()
