from __future__ import annotations

from django.apps import AppConfig


class EditableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_form_editable'
    name = 'django_spire.form.editable'
