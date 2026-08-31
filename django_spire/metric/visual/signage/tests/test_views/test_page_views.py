from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.models import SlideSection
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_slide,
)
from django_spire.metric.visual.signage.tests.factories import (
    create_test_link,
    create_test_signage,
    create_test_signage_links,
)
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
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

    def test_display_view_forwards_chart_update_interval(self):
        presentation = create_test_presentation(name='chart_board')
        slide = create_test_slide(presentation, order=0)
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)
        SlideSection.objects.create(slide=slide, visual=visual, row=1, col=1)
        create_test_link(self.signage, presentation=presentation, order=0)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:page:display', kwargs={'key': self.signage.key}
            )
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-chart-update-interval="15"' in content
        assert '_update_interval: 15' in content
