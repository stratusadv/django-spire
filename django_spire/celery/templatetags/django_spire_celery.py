from __future__ import annotations

from django import template
from django.template.loader import get_template

from django_spire.celery.manager import BaseCeleryTaskManager

register = template.Library()


def _render_django_spire_celery_task_template(
    celery_task_managers: list[BaseCeleryTaskManager], template_name: str
) -> str | None:
    if isinstance(celery_task_managers, list) and len(celery_task_managers) > 0:
        if isinstance(celery_task_managers[0], BaseCeleryTaskManager):
            return get_template(template_name).render(
                {
                    'django_spire_celery_task_key_pairs': ','.join(
                        [
                            celery_task_manager.reference_and_model_key
                            for celery_task_manager in celery_task_managers
                        ]
                    )
                }
            )

    return None


@register.simple_tag
def django_spire_celery_task_toast_widget(
    celery_task_managers: list[BaseCeleryTaskManager],
) -> str | None:
    return _render_django_spire_celery_task_template(
        celery_task_managers, template_name='django_spire/celery/toast/task_toast_widget.html'
    )


@register.simple_tag
def django_spire_celery_task_item_block(
    celery_task_managers: list[BaseCeleryTaskManager],
) -> str | None:
    return _render_django_spire_celery_task_template(
        celery_task_managers, template_name='django_spire/celery/item/task_item_block.html'
    )
