import json

from django import forms
from django.contrib import admin

from django_spire.ai import models


@admin.register(models.AiUsage)
class AiUsageAdmin(admin.ModelAdmin):
    list_display = ('recorded_date', 'compute_seconds', 'token_usage')
    search_fields = ('recorded_date',)
    ordering = ('-recorded_date',)


class InteractionField(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = 'spire/ai/forms/widgets/ai_interaction_widget.html'

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        if context['widget']['value'] is None:
            context['interaction_dict'] = {}
        else:
            context['interaction_dict'] = json.loads(context['widget']['value'])

        return context


class AiInteractionModelForm(forms.ModelForm):
    interaction = forms.JSONField(widget=InteractionField)

    class Meta:
        model = models.AiInteraction
        fields = '__all__'


@admin.register(models.AiInteraction)
class AiInteractionAdmin(admin.ModelAdmin):
    form = AiInteractionModelForm

    list_display = ('actor', 'module_name', 'callable_name', 'created_datetime', 'was_successful')
    list_filter = ('module_name', 'callable_name')
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
