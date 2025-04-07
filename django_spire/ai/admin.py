import json

from django import forms
from django.contrib import admin

from django_spire.ai import models


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
            for i, event in enumerate(context['interaction_dict']['event_manager']['events']):
                context['interaction_dict']['event_manager']['events'][i]['things'] = context['interaction_dict']['event_manager']['events'][i].pop('items')

        return context

class AiInteractionModelForm(forms.ModelForm):
    interaction = forms.JSONField(widget=InteractionField)

    class Meta:
        model = models.AiInteraction
        fields = '__all__'

@admin.register(models.AiInteraction)
class AiInteractionAdmin(admin.ModelAdmin):
    form = AiInteractionModelForm

    list_display = ('user_email', 'module_name', 'callable_name', 'created_datetime', 'was_successful')
    list_filter = ('module_name', 'callable_name')
    search_fields = ('user_email', 'user_first_name', 'user_last_name', 'module_name', 'callable_name')
    ordering = ('-created_datetime',)

