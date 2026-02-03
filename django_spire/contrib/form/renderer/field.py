from abc import ABC
from typing import Any

from django.forms import Field


class BaseFieldRenderer(ABC):
    def __init__(self, field_name: str, field: Field, value: Any = None):
        self.field_name = field_name
        self.field = field
        self.value = value or self.field.initial

    def render_js(self):
        return ''

    def render_html(self):
        return ''
