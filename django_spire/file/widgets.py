from __future__ import annotations

import json

from django.forms import Widget
from django.template import loader
from django.utils.safestring import SafeString, mark_safe


class MultipleFileWidget(Widget):
    needs_multipart_form = True
    template_name = 'django_spire/file/widget/multiple_file_widget.html'

    def render(
        self,
        name: str,
        value: str | None,
        attrs: dict | None = None,
        _renderer: object | None = None,
    ) -> SafeString:
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)  # noqa: S308

    def value_from_datadict(self, data: dict, files: dict, name: str) -> list[dict]:
        json_data = data.get(f'{name}_data')

        if json_data is not None:
            try:
                return json.loads(json_data)
            except (json.JSONDecodeError, TypeError):
                return []

        if files:
            return files.getlist(name)

        return []


class SingleFileWidget(Widget):
    needs_multipart_form = True
    template_name = 'django_spire/file/widget/single_file_widget.html'

    def render(
        self,
        name: str,
        value: str | None,
        attrs: dict | None = None,
        _renderer: object | None = None,
    ) -> SafeString:
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)  # noqa: S308

    def value_from_datadict(self, data: dict, files: dict, name: str) -> dict | None:
        json_data = data.get(f'{name}_data')

        if json_data is not None:
            try:
                return json.loads(json_data)
            except (json.JSONDecodeError, TypeError):
                return None

        if files and name in files:
            return files[name]

        return None
