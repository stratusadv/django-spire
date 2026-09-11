from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.activity.context import activity_user
from django_spire.metric.visual.charts import VisualLineChart
from django_spire.metric.visual.models import VisualRegion
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
        assert 'Glue.querySet.visuals' in response.content.decode()

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

    def test_detail_view_lists_regions(self):
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )

        assert response.status_code == 200
        assert region in response.context_data['visual'].regions.all()
        assert 'Assigned Regions' in response.content.decode()
        assert 'home:dashboard:hero' in response.content.decode()

    def test_detail_view_includes_visual_and_child_activities(self):
        condition = self.visual.conditions.first()
        reference = self.visual.references.create(reference='/home/', order=0)
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)

        with activity_user(self.super_user):
            condition.set_deleted()

        reference.add_activity(self.super_user, 'created', 'reference created')
        region.add_activity(self.super_user, 'updated', 'region updated')

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )

        assert response.status_code == 200
        activity_log = response.context_data['activity_log']
        assert set(activity_log.values_list('pk', flat=True)) == {
            condition.activities.get(verb='deleted').pk,
            reference.activities.first().pk,
            region.activities.first().pk,
        }

        content = response.content.decode()
        assert 'deleted Visual Condition' in content
        assert 'reference created' in content
        assert 'region updated' in content
