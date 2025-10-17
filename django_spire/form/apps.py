from __future__ import annotations

from django.apps import AppConfig


class FormConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_form'
    name = 'django_spire.form'

    REQUIRED_APPS = ('django_spire_core',)

    URLPATTERNS_INCLUDE = 'django_spire.form.urls'
    URLPATTERNS_NAMESPACE = 'form'
