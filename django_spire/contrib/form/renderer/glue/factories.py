from typing import Any

from django import forms

from django_spire.contrib.form.renderer.glue import maps


def create_glue_renderer_from_django_field(
    field_name: str,
    field: forms.Field,
    value: Any
):
    glue_renderer_class = maps.DJANGO_FIELD_TO_GLUE_FIELD_RENDERER_MAP[field.__class__]
    return glue_renderer_class(field_name, field, value)