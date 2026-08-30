from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

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
from django_spire.metric.visual.models import Visual, VisualCondition
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

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)

    def test_date_range_daily(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

        assert visual.services.transformation.date_range() == (date(2026, 5, 15), date(2026, 5, 15))

    def test_date_range_weekly(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

        start_date, end_date = visual.services.transformation.date_range()
        assert start_date == date(2026, 5, 10)
        assert end_date == date(2026, 5, 16)

    def test_date_range_monthly(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

        start_date, end_date = visual.services.transformation.date_range()
        assert start_date == date(2026, 5, 1)
        assert end_date == date(2026, 5, 31)

    def test_current_value_monthly_total(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.MONTHLY
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

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

        assert visual.services.transformation.current_value() == Decimal(100)

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

    def test_series_data_ordered_and_reference_filtered(self):
        statistic = create_test_statistic(
            group=self.group, interval=StatisticIntervalChoices.WEEKLY
        )
        visual = create_test_visual(statistic=statistic, reference='/home/', with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

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

        points = visual.services.transformation.series_data()

        assert points == [
            {'timestamp': date(2026, 5, 14), 'value': 10.0},
            {'timestamp': date(2026, 5, 15), 'value': 20.0},
        ]

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
        visual.date = date(2026, 5, 15)
        visual.save()

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

        datasets = visual.services.transformation.series_datasets()

        assert datasets == [
            {'label': 'Home', 'points': [{'timestamp': date(2026, 5, 14), 'value': 10.0}]},
            {'label': 'Dashboard', 'points': [{'timestamp': date(2026, 5, 15), 'value': 55.0}]},
        ]

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
        visual.date = date(2026, 5, 15)
        visual.save()

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

        datasets = visual.services.transformation.series_datasets()

        assert datasets == [
            {
                'label': 'Helpdesk Pages',
                'points': [
                    {'timestamp': date(2026, 5, 14), 'value': 10.0},
                    {'timestamp': date(2026, 5, 15), 'value': 20.0},
                ],
            }
        ]

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

    def test_current_value_percentage_is_moving_average(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        visual = create_test_visual(statistic=statistic, with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

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

        assert visual.services.transformation.current_value() == Decimal(5)

    def test_series_data_percentage_rolling_average(self):
        statistic = create_test_statistic(
            group=self.group, value_type=StatisticValueTypeChoices.PERCENTAGE
        )
        visual = create_test_visual(statistic=statistic, reference='/home/', with_conditions=False)
        visual.date = date(2026, 5, 15)
        visual.save()

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

        points = visual.services.transformation.series_data()

        assert points == [
            {'timestamp': date(2026, 5, 14), 'value': 4.0},
            {'timestamp': date(2026, 5, 15), 'value': 5.0},
        ]

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

    def test_gauge_max_derived_from_conditions(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, target=Decimal(200), tolerance=Decimal(50))

        assert visual.services.transformation.gauge_max() == 250

    def test_gauge_max_falls_back_to_value(self):
        statistic = create_test_statistic(group=self.group)
        visual = create_test_visual(statistic=statistic, with_conditions=False)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(40), sub_domain=self.sub_domain
        )

        assert visual.services.transformation.gauge_max() == 80

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
