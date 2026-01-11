from django_spire.metric.report.models import ReportRun
from django.contrib import admin


@admin.register(ReportRun)
class ReportRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_key_stack_verbose', 'datetime')
    ordering = ('-datetime',)
