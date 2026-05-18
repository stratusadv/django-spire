from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.celery.models import CeleryTask


class CeleryTaskQueueService(BaseDjangoModelService['CeleryTask']):
    obj: CeleryTask

    def get_estimated_queue_size(self) -> int:
        return self.obj_class.objects.by_unready().count()

    def get_estimated_queue_time_seconds(self) -> int:
        celery_tasks = self.obj_class.objects.by_completed()[:100]
        queue_times_seconds = [celery_task.queue_time_seconds for celery_task in celery_tasks]

        return int(sum(queue_times_seconds) / len(queue_times_seconds))