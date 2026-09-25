from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.urls import reverse
from django.utils import timezone

if TYPE_CHECKING:
    from django.http import HttpResponse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.activity.context import activity_user
from django_spire.metric.domain.statistic.constants import StatisticIntervalChoices
from django_spire.metric.visual.charts import VisualLineChart
from django_spire.metric.visual.models import Visual, VisualRegion
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
    create_test_visual,
)


def aware(value_date: date, hour: int = 12) -> datetime:
    return timezone.make_aware(
        datetime(value_date.year, value_date.month, value_date.day, hour)  # noqa: DTZ001
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
        assert "proxy.execute({'kwargs': this._params || {}})" in response.content.decode()

    def test_detail_view_missing_value_date_renders_today(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )

        assert response.status_code == 200
        assert response.context_data['value_date'] is None
        assert response.context_data['period_end'] == timezone.localdate()
        assert response.context_data['period_start'] == timezone.localdate() - timedelta(days=7)
        assert response.context_data['display_unit_label'] == '8 day(s)'
        assert '8 day(s)' in response.content.decode()

    def test_detail_view_invalid_value_date_renders_today(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk}),
            {'value_date': 'not-a-date'},
        )

        assert response.status_code == 200
        assert response.context_data['value_date'] is None
        assert response.context_data['period_end'] == timezone.localdate()

    def test_detail_view_future_value_date_renders_today(self):
        future = timezone.localdate() + timedelta(days=1)
        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk}),
            {'value_date': future.isoformat()},
        )

        assert response.status_code == 200
        assert response.context_data['value_date'] is None
        assert response.context_data['period_end'] == timezone.localdate()

    def test_detail_view_value_date_renders_picked_period(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        sub_domain = create_test_subdomain(domain=domain)
        statistic = create_test_statistic(group=group, interval=StatisticIntervalChoices.WEEKLY)
        visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(999),
            sub_domain=sub_domain,
            value_timestamp=aware(date(2026, 5, 8), 12),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 10),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(20),
            sub_domain=sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 11),
        )

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk}),
            {'value_date': '2026-05-15'},
        )

        assert response.status_code == 200
        assert response.context_data['value_date'] == date(2026, 5, 15)
        assert response.context_data['period_start'] == date(2026, 2, 22)
        assert response.context_data['period_end'] == date(2026, 5, 16)
        assert response.context_data['current_value'] == Decimal(30)
        assert response.context_data['chart'].params == {
            'visual_pk': visual.pk,
            'value_date': '2026-05-15',
        }
        assert 'value="2026-05-15"' in response.content.decode()

    def test_detail_view_no_matching_data_shows_caption(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        sub_domain = create_test_subdomain(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, reference='/live/')

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=sub_domain
        )

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk})
        )

        assert response.status_code == 200
        assert response.context_data['no_matching_data'] is True
        assert response.context_data['current_condition'] is None
        assert 'No matching data' in response.content.decode()

    def test_detail_view_matching_reference_has_no_caption(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        sub_domain = create_test_subdomain(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, reference='/home/')

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=sub_domain
        )

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk})
        )

        assert response.status_code == 200
        assert response.context_data['no_matching_data'] is False
        assert 'No matching data' not in response.content.decode()

    def test_detail_view_renders_browse_form_when_statistic_set(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )

        content = response.content.decode()
        assert 'name="value_date"' in content
        assert f'max="{timezone.localdate().isoformat()}"' in content

    def test_detail_view_without_statistic_has_no_browse_form(self):
        visual = Visual.objects.create(name='no statistic')

        response = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk})
        )

        assert response.status_code == 200
        assert 'name="value_date"' not in response.content.decode()

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


class VisualChartExecuteTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        sub_domain = create_test_subdomain(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)
        self.sub_domain = sub_domain

    @staticmethod
    def _chart_manifest(response: HttpResponse) -> dict:
        match = re.search(
            r'<script id="django-glue-context" type="application/json">(.*?)</script>',
            response.content.decode(),
            re.DOTALL,
        )
        manifest_list = json.loads(match.group(1))['manifest_list']

        return next(
            manifest
            for manifest in manifest_list
            if isinstance(manifest['metadata'].get('params'), list)
        )

    def _call_execute(self, manifest: dict, call_kwargs: dict) -> HttpResponse:
        return self.client.post(
            '/__dg__/callable_attribute/visual_line_chart/execute/',
            data={
                'policy_token': manifest['policy_token'],
                'state': '{}',
                'attribute': 'execute',
                'kwargs': json.dumps(call_kwargs),
            },
        )

    def test_execute_rebuilds_option_with_wrapped_params(self):
        self.visual.statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 10),
        )
        self.visual.statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(20),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 11),
        )
        page = self.client.get(
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': self.visual.pk})
        )
        manifest = self._chart_manifest(page)

        response = self._call_execute(
            manifest, {'kwargs': {'visual_pk': self.visual.pk, 'value_date': '2026-05-15'}}
        )

        assert response.status_code == 200
        data = response.json()['result']['result']['series'][0]['data']
        assert len(data) == 8
        assert data[-2:] == [['2026-05-14', 10.0], ['2026-05-15', 20.0]]
