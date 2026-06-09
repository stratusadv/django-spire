from __future__ import annotations

from datetime import UTC

from celery import states
from celery.result import AsyncResult
from django.db.models import F
from django.utils.timezone import make_aware, is_naive
from typing import TYPE_CHECKING

from django_spire.celery.services.queue_service import CeleryTaskQueueService
from django_spire.contrib.constructor.service import BaseDjangoModelService
from sqlalchemy.exc import OperationalError, DatabaseError

if TYPE_CHECKING:
    from django_spire.celery.models import CeleryTask


class CeleryTaskService(BaseDjangoModelService['CeleryTask']):
    obj: CeleryTask

    queue = CeleryTaskQueueService()

    def update_result(self, async_result: AsyncResult) -> None:
        if async_result.state == states.SUCCESS:  # This is to prevent race based mutations
            try:
                self.obj.result = async_result.get()

                date_done = async_result.date_done

                if is_naive(date_done):
                    date_done_aware = make_aware(date_done, UTC)
                else:
                    date_done_aware = date_done

                self.obj.completed_datetime = date_done_aware

                if self.obj.started_datetime is None:
                    self.obj.started_datetime = self.obj.queued_datetime

                self.obj.state = states.SUCCESS

            except (OperationalError, DatabaseError):
                if self.obj._result_capture_attempts > 3:
                    self.obj.state = states.FAILURE
                else:
                    self.obj._result_capture_attempts = F('_result_capture_attempts') + 1

    def update_from_async_result_and_save_if_change(self) -> None:
        has_changed = False

        async_result = self.obj.async_result

        new_meta = async_result.info  # This is to prevent race based mutations

        if self.obj._task_meta != new_meta:
            if async_result.ready():
                completed_meta = self.obj.meta
                completed_meta.set_completed()
                self.obj.meta = completed_meta.model_dump()
            else:
                self.obj._task_meta = new_meta

            if self.obj.started_datetime is None and self.obj.meta.started_datetime:
                self.obj.started_datetime = self.obj.started_datetime

            has_changed = True

        new_state = async_result.state  # This is to prevent race based mutations

        if self.obj.state != states.SUCCESS and new_state == states.SUCCESS:
            self.update_result(async_result)
            has_changed = True

        elif self.obj.state != new_state:
            self.obj.state = new_state
            has_changed = True

        if has_changed:
            self.obj.save()
