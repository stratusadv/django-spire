from django.db import models
from django.utils.timezone import now

from django_spire.metric.report.querysets import ReportRunQuerySet


class ReportRun(models.Model):
    report_key_stack = models.TextField()
    datetime = models.DateTimeField(default=now)

    objects = ReportRunQuerySet.as_manager()

    @property
    def report_button_text(self) -> str:
        return self.report_key_stack.split('|')[-1]

    @property
    def report_key_stack_verbose(self):
        return self.report_key_stack.replace('|', ' > ')

    class Meta:
        verbose_name = 'Report Run'
        verbose_name_plural = 'Report Runs'
        db_table = 'django_spire_metric_report_run'
