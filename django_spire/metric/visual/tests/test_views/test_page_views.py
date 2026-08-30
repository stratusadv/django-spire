from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.charts import VisualLineChart
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class VisualPageViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)

    def test_list_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:page:list'))
        assert response.status_code == 200
        assert self.visual in response.context_data['visuals']

    def test_detail_view(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )

        assert response.status_code == 200
        assert response.context_data['visual'] == self.visual
        assert response.context_data['current_condition'] is not None
        assert 'chart' not in response.context_data

    def test_detail_view_links_statistic(self):
        statistic_href = reverse(
            'django_spire:metric:domain:statistic:page:detail',
            kwargs={'pk': self.visual.statistic.pk},
        )

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )

        assert response.status_code == 200
        assert f'href="{statistic_href}"' in response.content.decode()

    def test_detail_view_with_chart_kind(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        chart_visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': chart_visual.pk})
        )

        assert response.status_code == 200
        assert isinstance(response.context_data['chart'], VisualLineChart)
