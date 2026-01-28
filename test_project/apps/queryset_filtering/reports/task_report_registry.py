from django_spire.metric.report import ReportRegistry
from test_project.apps.queryset_filtering.reports.sub_task_report_registry import SubTaskReportRegistry

from test_project.apps.queryset_filtering.reports.task_counting_monthly_report import TaskCountingMonthlyReport

class TaskReportRegistry(ReportRegistry):
    category = 'Queryset Tasks'
    report_names_classes = {
            'Counting Monthly': TaskCountingMonthlyReport,
            'Counting Monthly Again': TaskCountingMonthlyReport
    }
    report_registries = [
        SubTaskReportRegistry
    ]