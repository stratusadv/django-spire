from django_spire.metric.report.registry import ReportRegistry

from test_project.apps.queryset_filtering.reports.task_counting_monthly_report import TaskCountingMonthlyReport

class SubTaskReportRegistry(ReportRegistry):
    category = 'Sub Queryset Tasks'
    report_names_classes = {
            'Sub Counting Monthly': TaskCountingMonthlyReport
    }