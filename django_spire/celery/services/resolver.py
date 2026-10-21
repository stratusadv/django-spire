from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from celery import states

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.celery.models import CeleryTask

logger = logging.getLogger(__name__)


def resolve_celery_tasks(celery_tasks: QuerySet[CeleryTask], *, limit: int | None = None) -> int:
    changed = 0
    attempts = 0

    for celery_task in celery_tasks.order_by('queued_datetime', 'pk'):
        if limit is not None and attempts >= limit:
            break

        if celery_task.state in states.READY_STATES:
            continue

        attempts += 1
        previous_state = celery_task.state

        try:
            celery_task.services.update_from_backend()
        except Exception:
            logger.warning(
                'Failed to resolve CeleryTask %s from the backend',
                celery_task.task_id,
                exc_info=True,
            )
            continue

        if celery_task.state != previous_state:
            changed += 1

    return changed
