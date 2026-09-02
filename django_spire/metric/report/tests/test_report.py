from datetime import datetime
from typing import Any

from django.test import TestCase, override_settings
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.report.models import ReportRun
from django_spire.metric.report.registry import ReportRegistry
from django_spire.metric.report.report import BaseReport, ReportCell
from django_spire.metric.report.enums import ColumnType
from test_project.app.task.reports.task_counting_monthly_report import (
    TaskCountingMonthlyReport,
)

REPORT_INCLUDE = 'django_spire.metric.report.tests.test_report.DemoReportRegistry'


class DemoReport(BaseReport):
    title = 'Demo Report'

    captured_kwargs: list[dict[str, Any]] = []

    def team_choices(self):
        return (('sales', 'Sales'), ('marketing', 'Marketing'))

    def run(
        self,
        start_date: datetime,
        count: int = 3,
        show_total: bool = True,
        team: list = ('sales',),
    ) -> None:
        type(self).captured_kwargs.append(
            {
                'start_date': start_date,
                'count': count,
                'show_total': show_total,
                'team': team,
            }
        )
        self.add_column(
            title='Amount',
            type=self.ColumnType.DOLLAR_2,
            sub_type=self.ColumnType.NUMBER_2,
        )
        self.add_row(cell_values=[1.5], cell_sub_values=[2.5])


class NestedDemoReport(BaseReport):
    title = 'Nested Demo Report'

    def run(self, _count: int = 1) -> None:
        self.add_column(title='N')


class DemoNestedRegistry(ReportRegistry):
    category = 'Nested'
    report_names_classes = {'Nested Demo': NestedDemoReport}


class DemoReportRegistry(ReportRegistry):
    category = 'Metrics'
    report_names_classes = {'Demo': DemoReport}
    report_registries = [DemoNestedRegistry]


class ReportFrameworkTestCase(TestCase):
    def test_add_column_with_column_type(self):
        report = DemoReport()
        report.add_column(title='Amount', type=ColumnType.DOLLAR_2)

        assert report.columns[0].title == 'Amount'
        assert report.columns[0].type == ColumnType.DOLLAR_2
        assert report.column_count == 1
        assert report.is_ready

    def test_cell_value_verbose_formats_per_precision(self):
        assert ReportCell.cell_value_verbose(1234.5, ColumnType.DOLLAR) == '$1,234'
        assert ReportCell.cell_value_verbose(1234.5, ColumnType.DOLLAR_2) == '$1,234.50'
        assert ReportCell.cell_value_verbose(1234.5, ColumnType.DOLLAR_3) == '$1,234.500'
        assert ReportCell.cell_value_verbose(0.1234, ColumnType.PERCENT_2) == '0.12%'
        assert ReportCell.cell_value_verbose(1234.567, ColumnType.NUMBER_1) == '1,234.6'
        assert ReportCell.cell_value_verbose('plain', ColumnType.TEXT) == 'plain'

    def test_add_row_rejects_span_with_multiple_values(self):
        report = DemoReport()
        report.add_column(title='A')

        try:
            report.add_row([1, 2], span_all_columns=True)
        except ValueError:
            pass
        else:
            message = 'expected span validation to raise'
            raise AssertionError(message)

    def test_add_row_rejects_value_column_mismatch(self):
        report = DemoReport()
        report.add_column(title='A')
        report.add_column(title='B')

        try:
            report.add_row([1, 2, 3])
        except ValueError:
            pass
        else:
            message = 'expected value count mismatch to raise'
            raise AssertionError(message)

    def test_run_arguments_with_required_default_and_choices(self):
        report = DemoReport()
        arguments = report.run_arguments

        assert arguments['start_date']['required'] is True
        assert arguments['start_date']['annotation'] == 'datetime'
        assert arguments['count']['default'] == 3
        assert arguments['count']['required'] is False
        assert arguments['count']['annotation'] == 'int'
        assert arguments['show_total']['annotation'] == 'bool'
        assert arguments['team']['annotation'] == 'multi_select'
        assert ('sales', 'Sales') in arguments['team']['choices']

    def test_report_title_required(self):
        class UntitledReport(BaseReport):
            title = ''

            def run(self, **kwargs) -> None:
                pass

        try:
            UntitledReport()
        except ValueError:
            pass
        else:
            message = 'expected missing title to raise'
            raise AssertionError(message)


class ReportRegistryTestCase(TestCase):
    def _registry(self) -> ReportRegistry:
        registry = ReportRegistry()
        registry.add_registry(DemoReportRegistry())
        return registry

    def test_resolves_nested_report_from_key_stack(self):
        report = self._registry().get_report_from_key_stack('Metrics|Nested|Nested Demo')

        assert isinstance(report, NestedDemoReport)

    def test_unknown_key_stack_returns_none(self):
        assert self._registry().get_report_from_key_stack('Does|Not|Exist') is None

    def test_category_only_key_stack_returns_none(self):
        assert self._registry().get_report_from_key_stack('Metrics') is None

    def test_registries_are_isolated_between_instances(self):
        first = ReportRegistry()
        second = ReportRegistry()

        first.add_registry(DemoReportRegistry())

        assert first.get_report_from_key_stack('Metrics|Demo') is not None
        assert second.get_report_from_key_stack('Metrics|Demo') is None


@override_settings(DJANGO_SPIRE_REPORT_REGISTRIES=[REPORT_INCLUDE])  # type: ignore[assignment]
class ReportViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        DemoReport.captured_kwargs.clear()
        self.url = reverse('django_spire:metric:report:page:report')
        self.key_stack = 'Metrics|Demo'

    def _run_url(self, invalid_start: bool = False) -> str:
        start_date = 'garbage' if invalid_start else '2024-01-15T00:00:00'

        return (
            f'{self.url}?report_key_stack={self.key_stack}&report_should_run=true'
            f'&start_date={start_date}&count=5&show_total=true'
        )

    def test_report_page_lists_top_runs(self):
        response = self.client.get(self.url)

        assert response.status_code == 200
        assert 'top_ten_report_runs' in response.context_data

    def test_missing_required_argument_marks_missing(self):
        url = f'{self.url}?report_key_stack={self.key_stack}&report_should_run=true&count=5'

        response = self.client.get(url)

        assert response.status_code == 200
        assert 'start_date' in response.context_data['report_missing_arguments']
        assert ReportRun.objects.count() == 0

    def test_invalid_argument_value_marks_invalid(self):
        response = self.client.get(self._run_url(invalid_start=True))

        assert 'start_date' in response.context_data['report_invalid_arguments']
        assert response.context_data['report_run_arguments_values']['start_date'] is None

    def test_running_report_creates_report_run_and_passes_coerced_args(self):
        response = self.client.get(self._run_url())

        assert response.status_code == 200
        assert ReportRun.objects.filter(report_key_stack=self.key_stack).count() == 1
        assert response.context_data['report_run_count'] == 1

        captured = DemoReport.captured_kwargs[-1]

        assert isinstance(captured['start_date'], datetime)
        assert captured['count'] == 5
        assert captured['show_total'] is True

    def test_report_registry_does_not_leak_between_requests(self):
        self.client.get(self._run_url())
        response = self.client.get(self._run_url())

        assert response.context_data['report_run_count'] == 2
        report = response.context_data['report']

        assert isinstance(report, DemoReport)


@override_settings(
    DJANGO_SPIRE_REPORT_REGISTRIES=[  # type: ignore[assignment]
        'test_project.app.task.reports.task_report_registry.TaskReportRegistry'
    ]
)
class TaskDemoReportViewTestCase(BaseTestCase):
    def test_task_report_arguments_render_without_error(self):
        url = reverse('django_spire:metric:report:page:report')

        response = self.client.get(f'{url}?report_key_stack=Queryset Tasks|Counting Monthly')

        assert response.status_code == 200
        assert 'start_date' in response.context_data['report_run_arguments']
        assert 'person' in response.context_data['report_run_arguments']

    def test_nested_task_report_resolves(self):
        url = reverse('django_spire:metric:report:page:report')

        response = self.client.get(
            f'{url}?report_key_stack=Queryset Tasks|Sub Queryset Tasks|Sub Counting Monthly'
        )

        assert response.status_code == 200
        assert isinstance(response.context_data['report'], TaskCountingMonthlyReport)