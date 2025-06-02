from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.ai import models
from django_spire.ai.mixins import AiUsageAdminMixin
from django_spire.core.forms.widgets import JsonTreeWidget


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
        'view_failed_interactions_link'
    )
    search_fields = ('recorded_date',)
    ordering = ('-recorded_date',)

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def view_interactions_link(
            self,
            ai_usage: models.AiUsage,
            was_successful: bool | None = None,
    ) -> str:
        was_successful_filter = '' if was_successful is None else f'&was_successful__exact={int(was_successful)}'
        url = (
                reverse("admin:django_spire_ai_aiinteraction_changelist")
                + "?"
                + urlencode({"ai_usage__id": f"{ai_usage.id}"})
                + was_successful_filter
        )

        if was_successful is None:
            interactions_count = ai_usage.interactions.count()
        elif was_successful:
            interactions_count = ai_usage.interactions.filter(was_successful=True).count()
        else:
            interactions_count = ai_usage.interactions.filter(was_successful=False).count()

        return format_html(
            f'<a href="{url}">{interactions_count} Interactions</a>'
        )

    view_interactions_link.short_description = "All"

    def view_successful_interactions_link(
            self,
            ai_usage: models.AiUsage,
    ) -> str:
        return self.view_interactions_link(ai_usage, was_successful=True)

    view_successful_interactions_link.short_description = "Successful"

    def view_failed_interactions_link(
            self,
            ai_usage: models.AiUsage,
    ) -> str:
        return self.view_interactions_link(ai_usage, was_successful=False)

    view_failed_interactions_link.short_description = "Failed"


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
    search_fields = ('actor', 'user_email', 'user_first_name', 'user_last_name', 'module_name', 'callable_name')
    ordering = ('-created_datetime',)

    readonly_fields = [
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
    ]
    fields = [
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
    ]
