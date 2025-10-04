from __future__ import annotations

from django.db import models

from django.contrib import admin


class AiUsageMixin(models.Model):
    event_count = models.IntegerField(default=0, verbose_name='Events')
    token_usage = models.IntegerField(default=0, verbose_name='Tokens')
    run_time_seconds = models.FloatField(default=0.0, verbose_name='Run Time')
    was_successful = models.BooleanField(default=True, verbose_name='Success')

    class Meta:
        abstract = True


class AiUsageAdminMixin(admin.ModelAdmin):
    def run_time_seconds_formatted(self, obj) -> str:
        return f"{obj.run_time_seconds:.3f}s"

    run_time_seconds_formatted.short_description = 'Run Time'
