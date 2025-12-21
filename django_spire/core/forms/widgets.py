from __future__ import annotations

import json
import uuid

from django import forms


class JsonTreeWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.template_name = 'django_spire/forms/widgets/json_tree_widget.html'

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['open_dropdowns'] = True
        context['widget_render_uuid'] = uuid.uuid4()

        if context['widget']['value'] is None:
            context['json_tree_dict'] = {}
        else:
            context['json_tree_dict'] = json.loads(context['widget']['value'])

        return context
