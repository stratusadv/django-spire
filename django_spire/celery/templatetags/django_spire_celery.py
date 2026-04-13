from __future__ import annotations

from django import template
from django.db import models

from django.template.loader import get_template

from django_spire.celery.models import CeleryTask

register = template.Library()


@register.simple_tag
def django_spire_celery_task_toast_widget(
        app_name: str,
        reference_name: str,
        model_object: models.Model | None = None,
):
    CeleryTask.validate_register_arguments(
        app_name=app_name,
        reference_name=reference_name,
    )

    reference_key = CeleryTask.generate_reference_key(
        app_name=app_name,
        reference_name=reference_name,
        model_object=model_object,
    )

    context = {
        'django_spire_celery_task_reference_key': reference_key,
    }

    return get_template(
        'django_spire/celery/toast/task_toast_widget.html'
    ).render(
        context
    )