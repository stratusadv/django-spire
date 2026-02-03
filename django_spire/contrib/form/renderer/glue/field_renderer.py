from __future__ import annotations

import json
from abc import ABC
from typing import Any

from django import forms

from django.forms import Field

from django_spire.contrib.form.renderer.field import BaseFieldRenderer
from django_spire.contrib.form.renderer.glue import maps


class BaseSpireGlueFieldRenderer(BaseFieldRenderer, ABC):
    glue_field_name: str = ''
    field_template_name: str = ''
    js_template = "{field_name}: new {glue_field_name}('{field_name}', {field_options}),"
    html_template = 'django_spire/form/field/{field_template_name}.html'

    def get_glue_field_options(self, default_value: Any = None, **kwargs):
        options = {
            'value': default_value or self.field.initial or None,
            'name': self.field_name,
            'label': self.field.label,
            'required': self.field.required,
            'disabled': self.field.disabled,
            **kwargs
        }

        return {key: value for key, value in options.items() if value is not None}

    def render_js(self, default_value: Any = None, **kwargs) -> str:
        return self.js_template.format(
            self.js_template,
            field_name=self.field_name,
            glue_field_name=self.glue_field_name,
            field_options=json.dumps(
                self.get_glue_field_options(
                    default_value=default_value,
                    **kwargs
                ), indent=4
            )
        )

    def render_html(self):
        return self.html_template.format(
            field_template_name=self.field_template_name,
            field_name=self.field_name
        )

    @staticmethod
    def from_django_field(field_name: str, field: forms.Field):
        glue_renderer_class = maps.DJANGO_FIELD_TO_GLUE_FIELD_RENDERER_MAP[field.__class__]
        return glue_renderer_class(field_name, field)


class SpireGlueBooleanFieldRenderer(BaseSpireGlueFieldRenderer):
    glue_field_name = 'GlueBooleanField'
    field_template_name = 'single_checkbox_field'


class SpireGlueCharFieldRenderer(BaseSpireGlueFieldRenderer):
    glue_field_name = 'GlueCharField'
    field_template_name = 'char_field'

    def get_glue_field_options(self, **kwargs):
        return super().get_glue_field_options(**{
            'max_length': self.field.max_length,
            'min_length': self.field.min_length,
            **kwargs
        })


class SpireGlueChoiceFieldRenderer(BaseSpireGlueFieldRenderer):
    glue_field_name = 'GlueCharField'
    field_template_name = 'search_and_select_field'

    def get_glue_field_options(self, **kwargs):
        return super().get_glue_field_options(**{
            'max_length': self.field.max_length,
            'min_length': self.field.min_length,
            'choices': self.field.choices
            **kwargs
        })


class SpireGlueDateFieldRenderer(BaseSpireGlueFieldRenderer):
    glue_field_name = 'GlueDateField'
    field_template_name = 'date_field'

    def __init__(self, field_name: str, field: Field):
        if isinstance(field, forms.DateTimeField):
            self.field_template_name = 'datetime_field'

        super().__init__(field_name, field)

    def get_extra_glue_field_options(self, **kwargs):
        return super().get_glue_field_options({
            'max_length': self.field.max_length,
            'min_length': self.field.min_length,
            **kwargs
        })


class SpireGlueIntegerFieldRenderer(BaseSpireGlueFieldRenderer):
    glue_field_name = 'GlueIntegerField'
    field_template_name = 'number_field'

    def get_extra_glue_field_options(self, **kwargs):
        return super().get_glue_field_options({
            'max_length': self.field.max_length,
            'min_length': self.field.min_length,
            'step': self.field.step,
            **kwargs
        })


class GlueDecimalFieldRenderer(SpireGlueIntegerFieldRenderer):
    glue_field_name = 'GlueDecimalField'
