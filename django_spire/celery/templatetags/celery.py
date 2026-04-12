from __future__ import annotations

import json

from typing import Sequence

from django import template
from django.db import models

from django_spire.celery.models import CeleryTask

register = template.Library()


@register.simple_tag
def load_template(
        app_label: str,
        reference_name: str,
        model_object: models.Model | None = None,
):
    object_hash = CeleryTask.generate_hash(app_label, reference_name, model_object)

    celery_tasks = CeleryTask.objects.filter(
        object_hash=object_hash
    )

    context = {}

    from django.template.loader import get_template
    return get_template(
        'django_spire/celery/tasks_widget.html'
    ).render(
        context
    )


@register.filter(name='generate_hash')
def generate_hash(
        app_label: str,
        reference_name: str,
        model_object: models.Model | None = None,
) -> str:
    return CeleryTask.generate_hash(app_label, reference_name, model_object)
