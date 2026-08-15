from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django import forms
from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html

from django_spire.ai import models
from django_spire.ai.mixins import AiUsageAdminMixin
from django_spire.contrib.admin.links import admin_changelist_url
from django_spire.contrib.form.widgets import JsonTreeWidget

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django.http import HttpRequest


@admin.register(models.AiUsage)
class AiUsageAdmin(AiUsageAdminMixin):
    list_display = (
        'recorded_date',
        'was_successful',
        'event_count',
        'token_usage',
        'run_time_seconds_formatted',
        'view_interactions_link',
        'view_successful_interactions_link',
        'view_failed_interactions_link',
    )
    ordering = ('-recorded_date',)
    search_fields = ('recorded_date',)

    def _interactions_link(
        self,
        ai_usage: models.AiUsage,
        count: int,
        was_successful: bool | None = None,
    ) -> str:
        filters = {'ai_usage__id': str(ai_usage.id)}

        if was_successful is not None:
            filters['was_successful__exact'] = str(int(was_successful))

        url = admin_changelist_url(models.AiInteraction, **filters)

        return format_html('<a href="{}">{} Interactions</a>', url, count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.AiUsage]:
        queryset = super().get_queryset(request)

        return queryset.annotate(
            _interaction_count=Count('interaction', distinct=True),
            _successful_interaction_count=Count(
                'interaction',
                filter=Q(interaction__was_successful=True),
                distinct=True,
            ),
            _failed_interaction_count=Count(
                'interaction',
                filter=Q(interaction__was_successful=False),
                distinct=True,
            ),
        )

    def get_readonly_fields(self, request: HttpRequest, obj: Model | None = None) -> list[str]:
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @admin.display(description='Failed', ordering='_failed_interaction_count')
    def view_failed_interactions_link(self, ai_usage: models.AiUsage) -> str:
        return self._interactions_link(
            ai_usage,
            ai_usage._failed_interaction_count,
            was_successful=False,
        )

    @admin.display(description='All', ordering='_interaction_count')
    def view_interactions_link(self, ai_usage: models.AiUsage) -> str:
        return self._interactions_link(ai_usage, ai_usage._interaction_count)

    @admin.display(description='Successful', ordering='_successful_interaction_count')
    def view_successful_interactions_link(self, ai_usage: models.AiUsage) -> str:
        return self._interactions_link(
            ai_usage,
            ai_usage._successful_interaction_count,
            was_successful=True,
        )


class AiInteractionModelForm(forms.ModelForm):
    interaction = forms.JSONField(widget=JsonTreeWidget)

    class Meta:
        model = models.AiInteraction
        fields = '__all__'


@admin.register(models.AiInteraction)
class AiInteractionAdmin(AiUsageAdminMixin):
    form = AiInteractionModelForm

    list_display = (
        'actor',
        'callable_name',
        'was_successful',
        'event_count',
        'token_usage',
        'run_time_seconds_formatted',
        'created_datetime',
    )
    list_filter = ('module_name', 'callable_name', 'was_successful')
    ordering = ('-created_datetime',)
    search_fields = (
        'actor',
        'user_email',
        'user_first_name',
        'user_last_name',
        'module_name',
        'callable_name',
    )

    readonly_fields = (
        'actor',
        'created_datetime',
        'module_name',
        'callable_name',
        'was_successful',
        'user',
        'user_email',
        'user_first_name',
        'user_last_name',
        'exception',
        'stack_trace',
    )
    fields = (
        'actor',
        'user',
        'created_datetime',
        'module_name',
        'callable_name',
        'was_successful',
        'interaction',
        'user_email',
        'user_first_name',
        'user_last_name',
        'exception',
        'stack_trace',
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
