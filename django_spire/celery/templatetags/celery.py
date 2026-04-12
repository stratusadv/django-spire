from __future__ import annotations

from django import template
from django.db import models

from django.template.loader import get_template

from django_spire.celery.models import CeleryTask

register = template.Library()


@register.simple_tag
def celery_tasks_widget(
        app_label: str,
        reference_name: str,
        model_object: models.Model | None = None,
):
    object_hash = CeleryTask.generate_hash(app_label, reference_name, model_object)

    context = {
        'celery_task_object_hash': object_hash,
    }

    return get_template(
        'django_spire/celery/tasks_widget.html'
    ).render(
        context
    )