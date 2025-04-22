from __future__ import annotations

import json

from django.template import loader
from django.utils.safestring import mark_safe
from django.forms import Widget


class MultipleWidget(Widget):
    needs_multipart_form = True
    template_name = 'django_spire/file/widget/multiple_file_widget.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        return json.loads(data.get(f'{name}_data'))

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class SingleFileWidget(Widget):
    needs_multipart_form = True
    template_name = 'django_spire/file/widget/single_file_widget.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name) -> dict:
        return json.loads(data.get(f'{name}_data'))

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
