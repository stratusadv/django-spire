from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import mock

from django.core.cache import cache
from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.constants import (
    StatisticIntervalChoices,
    StatisticValueTypeChoices,
)
from django_spire.metric.visual.charts import (
    VisualAreaChart,
    VisualBarChart,
    VisualGaugeChart,
    VisualLineChart,
    VisualPieChart,
)
from django_spire.metric.visual.models import Visual, VisualCondition, VisualRegion
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


class VisualTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        cache.clear()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)

    def test_date_range_daily(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        assert visual.services.transformation.date_range(date(2026, 5, 15)) == (
            date(2026, 5, 15),
            date(2026, 5, 15),
        )

    def test_date_range_weekly(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        start_date, end_date = visual.services.transformation.date_range(date(2026, 5, 15))
        assert start_date == date(2026, 5, 10)
        assert end_date == date(2026, 5, 16)

    def test_date_range_monthly(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        start_date, end_date = visual.services.transformation.date_range(date(2026, 5, 15))
        assert start_date == date(2026, 5, 1)
        assert end_date == date(2026, 5, 31)

    def test_current_value_monthly_total(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(40),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 5)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(60),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 20)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(1000),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 6, 1)),
        )

        assert visual.services.transformation.current_value(date(2026, 5, 15)) == Decimal(100)

    def test_current_value_filters_reference(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, reference='/home/', with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(90), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.current_value() == Decimal(10)

    def test_current_value_without_statistic(self):
        visual = Visual.objects.create(name='empty')
        assert visual.services.transformation.current_value() == Decimal(0)

    def test_current_value_anchors_to_localdate(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        today = timezone.localdate()
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(today - timedelta(days=1)),
        )
        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(25), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.current_value() == Decimal(25)

    def test_daily_visual_recomputes_after_midnight_rollover(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        today = timezone.localdate()
        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        assert visual.services.transformation.current_value() == Decimal(10)

        with mock.patch(
            'django_spire.metric.visual.services.transformation_service.timezone.localdate',
            return_value=today + timedelta(days=1),
        ):
            assert visual.services.transformation.current_value() == Decimal(0)

    def test_cache_key_changes_with_date(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        today = timezone.localdate()
        key_today = visual.services.transformation._cache_key('value')
        key_next_day = visual.services.transformation._cache_key(
            'value', value_date=today + timedelta(days=1)
        )

        assert today.isoformat() in key_today
        assert key_today != key_next_day

    def test_display_window_defaults_per_interval(self):
        cases = {
            StatisticIntervalChoices.DAILY: (date(2026, 5, 8), date(2026, 5, 15)),
            StatisticIntervalChoices.WEEKLY: (date(2026, 2, 22), date(2026, 5, 16)),
            StatisticIntervalChoices.MONTHLY: (date(2025, 5, 1), date(2026, 5, 31)),
        }

        for interval, window in cases.items():
            statistic = create_test_statistic(group=self.group, interval=interval)
            visual = create_test_visual(statistic=statistic, with_conditions=False)

            assert visual.services.transformation.display_window(date(2026, 5, 15)) == window

    def test_display_window_uses_visual_count_override(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.display_unit_count = 3
        visual.save()

        assert visual.services.transformation.display_unit_count() == 3
        assert visual.services.transformation.display_window(date(2026, 5, 15)) == (
            date(2026, 5, 13),
            date(2026, 5, 15),
        )

    def test_display_window_without_statistic_is_value_date(self):
        visual = Visual.objects.create(name='empty')

        assert visual.services.transformation.display_window(date(2026, 5, 15)) == (
            date(2026, 5, 15),
            date(2026, 5, 15),
        )

    def test_display_unit_label_daily_default(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        assert visual.services.transformation.display_unit_label() == '8 day(s)'

    def test_display_unit_label_weekly_and_monthly_defaults(self):
        weekly_statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        monthly_statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        weekly_visual = create_test_visual(statistic=weekly_statistic, with_conditions=False)
        monthly_visual = create_test_visual(statistic=monthly_statistic, with_conditions=False)

        assert weekly_visual.services.transformation.display_unit_label() == '12 week(s)'
        assert monthly_visual.services.transformation.display_unit_label() == '13 month(s)'

    def test_display_unit_label_honors_count_override(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.display_unit_count = 3
        visual.save()

        assert visual.services.transformation.display_unit_label() == '3 day(s)'

    def test_display_unit_label_without_statistic_is_bare_count(self):
        visual = Visual.objects.create(name='empty')

        assert visual.services.transformation.display_unit_label() == '8'

    def test_current_condition_green(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, target=Decimal(100), tolerance=Decimal(10))

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(150), sub_domain=self.sub_domain
        )

        condition = visual.services.transformation.current_condition()
        assert condition.state == 'green'

    def test_current_condition_yellow(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, target=Decimal(100), tolerance=Decimal(10))

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(95), sub_domain=self.sub_domain
        )

        condition = visual.services.transformation.current_condition()
        assert condition.state == 'yellow'

    def test_current_condition_red(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, target=Decimal(100), tolerance=Decimal(10))

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(50), sub_domain=self.sub_domain
        )

        condition = visual.services.transformation.current_condition()
        assert condition.state == 'red'

    def test_current_condition_none_when_no_match(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        VisualCondition.objects.create(
            visual=visual, state='green', operator='gt', target=Decimal(100), order=0
        )

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(50), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.current_condition() is None

    def test_no_matching_data_flag_off_without_references(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.no_matching_data() is False

    def test_no_matching_data_flag_off_for_empty_statistic(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, reference='/live/', with_conditions=False)

        assert visual.services.transformation.no_matching_data() is False

    def test_render_context_no_matching_data_suppresses_condition(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, reference='/live/')

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )

        context = visual.services.transformation.render_context()

        assert context['no_matching_data'] is True
        assert context['current_value'] == Decimal(0)
        assert context['current_condition'] is None

    def test_series_data_ordered_and_reference_filtered(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        visual = create_test_visual(statistic=statistic, reference='/home/', with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 10),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(20),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 11),
        )
        statistic.services.processor.add_value(
            reference='/dashboard/',
            value=Decimal(200),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 12),
        )

        points = visual.services.transformation.series_data(date(2026, 5, 15))

        assert len(points) == 12
        assert points[-1] == {'timestamp': date(2026, 5, 10), 'value': 30.0}
        assert all(point['value'] == 0.0 for point in points[:-1])

    def test_series_datasets_multiple_references(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        visual = create_test_visual(
            statistic=statistic,
            references=['/home/', '/dashboard/'],
            labels=['Home', 'Dashboard'],
            with_conditions=False,
        )

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 10),
        )
        statistic.services.processor.add_value(
            reference='/dashboard/',
            value=Decimal(55),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 12),
        )

        datasets = visual.services.transformation.series_datasets(date(2026, 5, 15))

        assert [dataset['label'] for dataset in datasets] == ['Home', 'Dashboard']
        assert all(len(dataset['points']) == 12 for dataset in datasets)
        assert datasets[0]['points'][-1] == {'timestamp': date(2026, 5, 10), 'value': 10.0}
        assert datasets[1]['points'][-1] == {'timestamp': date(2026, 5, 10), 'value': 55.0}
        assert all(
            point['value'] == 0.0 for dataset in datasets for point in dataset['points'][:-1]
        )

    def test_series_datasets_wildcard_prefix(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        visual = create_test_visual(
            statistic=statistic,
            references=['helpdesk:page:%'],
            labels=['Helpdesk Pages'],
            with_conditions=False,
        )

        statistic.services.processor.add_value(
            reference='helpdesk:page:view',
            value=Decimal(10),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14), 10),
        )
        statistic.services.processor.add_value(
            reference='helpdesk:page:detail',
            value=Decimal(20),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 11),
        )
        statistic.services.processor.add_value(
            reference='helpdesk:ticket:view',
            value=Decimal(99),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 12),
        )

        datasets = visual.services.transformation.series_datasets(date(2026, 5, 15))

        assert [dataset['label'] for dataset in datasets] == ['Helpdesk Pages']
        points = datasets[0]['points']
        assert len(points) == 12
        assert points[-1] == {'timestamp': date(2026, 5, 10), 'value': 30.0}
        assert all(point['value'] == 0.0 for point in points[:-1])

    def test_current_value_uses_first_dataset_only(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(
            statistic=statistic, references=['/home/', '/dashboard/'], with_conditions=False
        )

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(90), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.current_value() == Decimal(10)

    def test_dataset_values_for_gauge(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(
            statistic=statistic, references=['/home/', '/dashboard/'], with_conditions=False
        )

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(90), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.dataset_values() == [
            {'label': '/home/', 'value': Decimal(10)},
            {'label': '/dashboard/', 'value': Decimal(90)},
        ]

    def test_series_data_without_statistic(self):
        visual = Visual.objects.create(name='empty', kind='line')
        assert visual.services.transformation.series_data() == []

    def test_series_data_honors_display_unit_count_override(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, reference='/home/', with_conditions=False)
        visual.display_unit_count = 3
        visual.save()

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(7), sub_domain=self.sub_domain
        )

        points = visual.services.transformation.series_data()

        assert len(points) == 3
        assert points[-1] == {'timestamp': timezone.localdate(), 'value': 7.0}

    def test_series_data_monthly_buckets_values(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(30),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 3, 10)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(20),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 20)),
        )

        points = visual.services.transformation.series_data(date(2026, 5, 15))

        assert len(points) == 13
        assert points[-3] == {'timestamp': date(2026, 3, 1), 'value': 30.0}
        assert points[-1] == {'timestamp': date(2026, 5, 1), 'value': 20.0}
        assert all(point['value'] == 0.0 for point in points[:-3])
        assert points[-2]['value'] == 0.0

    def test_series_breakdown_groups_by_reference(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(30), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(20), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(50), sub_domain=self.sub_domain
        )

        breakdown = visual.services.transformation.series_breakdown()

        assert {'name': '/dashboard/', 'value': 50.0} in breakdown
        assert {'name': '/home/', 'value': 50.0} in breakdown

    def test_series_breakdown_uses_reference_labels(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(
            statistic=statistic,
            references=['/home/', '/dashboard/'],
            labels=['Home', 'Dashboard'],
            with_conditions=False,
        )

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(30), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(50), sub_domain=self.sub_domain
        )

        breakdown = visual.services.transformation.series_breakdown()

        assert {'name': 'Home', 'value': 30.0} in breakdown
        assert {'name': 'Dashboard', 'value': 50.0} in breakdown

    def test_current_value_percentage_is_moving_average(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(4),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(6),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(100),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 1)),
        )

        assert visual.services.transformation.current_value(date(2026, 5, 15)) == Decimal(5)

    def test_series_data_percentage_uses_raw_unit_average(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        visual = create_test_visual(statistic=statistic, reference='/home/', with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(4),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 14)),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(6),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 10),
        )
        statistic.services.processor.add_value(
            reference='/home/',
            value=Decimal(8),
            sub_domain=self.sub_domain,
            value_timestamp=aware(date(2026, 5, 15), 12),
        )

        points = visual.services.transformation.series_data(date(2026, 5, 15))

        assert len(points) == 8
        assert points[-2] == {'timestamp': date(2026, 5, 14), 'value': 4.0}
        assert points[-1] == {'timestamp': date(2026, 5, 15), 'value': 7.0}
        assert all(point['value'] == 0.0 for point in points[:-2])

    def test_series_breakdown_percentage_averages_reference(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(20), sub_domain=self.sub_domain
        )
        statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(30), sub_domain=self.sub_domain
        )

        breakdown = visual.services.transformation.series_breakdown()

        assert {'name': '/dashboard/', 'value': 30.0} in breakdown
        assert {'name': '/home/', 'value': 15.0} in breakdown

    def test_gauge_max_is_100(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, target=Decimal(200), tolerance=Decimal(50))

        assert visual.services.transformation.gauge_max() == 100

    def test_current_value_is_cached(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.current_value() == Decimal(10)

        with self.assertNumQueries(2):
            assert visual.services.transformation.current_value() == Decimal(10)

    def test_current_value_cache_invalidated_by_new_value(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        assert visual.services.transformation.current_value() == Decimal(10)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(5), sub_domain=self.sub_domain
        )
        assert visual.services.transformation.current_value() == Decimal(15)

    def test_chart_returns_none_for_indicator(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        assert visual.services.transformation.chart() is None

    def test_chart_kind_mapping(self):
        statistic = create_test_statistic(group=self.group)

        cases = {
            'line': VisualLineChart,
            'bar': VisualBarChart,
            'area': VisualAreaChart,
            'pie': VisualPieChart,
            'gauge': VisualGaugeChart,
        }

        for kind, chart_class in cases.items():
            visual = create_test_visual(statistic=statistic, kind=kind, with_conditions=False)
            chart = visual.services.transformation.chart()
            assert isinstance(chart, chart_class)
            assert chart.params == {'visual_pk': visual.pk}

    def test_render_context_indicator(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, target=Decimal(100), tolerance=Decimal(10))

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(150), sub_domain=self.sub_domain
        )

        context = visual.services.transformation.render_context()

        assert context['visual'] == visual
        assert context['current_value'] == Decimal(150)
        assert context['current_condition'] is not None
        assert context['chart'] is None
        assert context['period_end'] == timezone.localdate()
        assert context['period_start'] == timezone.localdate() - timedelta(days=7)

    def test_render_context_chart(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)

        context = visual.services.transformation.render_context()

        assert context['visual'] == visual
        assert isinstance(context['chart'], VisualLineChart)

    def test_render_context_for_deleted_visual_is_empty(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.set_deleted()

        context = visual.services.transformation.render_context()

        assert context['visual'] is None
        assert context['current_value'] is None
        assert context['current_condition'] is None
        assert context['chart'] is None

    def test_aggregates_are_empty_for_deleted_statistic(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        statistic.set_deleted()

        assert visual.services.transformation.current_value() == Decimal(0)
        assert visual.services.transformation.series_datasets() == []
        assert visual.services.transformation.series_breakdown() == []
        assert visual.services.transformation.dataset_values() == []

    def test_render_context_is_empty_for_deleted_statistic(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, kind='line', with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=self.sub_domain
        )
        statistic.set_deleted()

        context = visual.services.transformation.render_context()

        assert context['visual'] is None
        assert context['current_value'] is None
        assert context['current_condition'] is None
        assert context['chart'] is None


class VisualRegionTransformationServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        cache.clear()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)

    def test_display_title_uses_title(self):
        region = VisualRegion.objects.create(
            key='home:dashboard:hero', visual=self.visual, title='Hero'
        )
        assert region.services.transformation.display_title == 'Hero'

    def test_display_title_falls_back_to_visual_name(self):
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)
        assert region.services.transformation.display_title == self.visual.name

    def test_display_title_falls_back_to_key(self):
        region = VisualRegion.objects.create(key='dashboard:empty')
        assert region.services.transformation.display_title == 'dashboard:empty'

    def test_render_context_with_visual(self):
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)

        context = region.services.transformation.render_context()

        assert context['visual'] == self.visual
        assert context['display_title'] == self.visual.name
        assert 'current_value' in context

    def test_render_context_without_visual(self):
        region = VisualRegion.objects.create(key='dashboard:empty')

        context = region.services.transformation.render_context()

        assert context['visual'] is None
        assert context['current_value'] is None
        assert context['display_title'] == 'dashboard:empty'
