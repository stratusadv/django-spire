from __future__ import annotations

from datetime import timezone

from celery import states
from celery.result import AsyncResult
from django.db.models import F
from django.utils.timezone import make_aware, is_naive
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from sqlalchemy.exc import OperationalError, DatabaseError

if TYPE_CHECKING:
    from django_spire.celery.models import CeleryTask


class CeleryTaskService(BaseDjangoModelService['CeleryTask']):
    obj: CeleryTask

    def update_result(self, async_result: AsyncResult) -> None:
        if async_result.state == states.SUCCESS:
            try:
                self.obj.result = async_result.get()

                date_done = async_result.date_done

                if is_naive(date_done):
                    date_done_aware = make_aware(date_done, timezone.utc)
                else:
                    date_done_aware = date_done

                self.obj.completed_datetime = date_done_aware
                self.obj.state = states.SUCCESS

            except (OperationalError, DatabaseError):
                if self.obj._result_capture_attempts > 3:
                    self.obj.state = states.FAILURE
                else:
                    self.obj._result_capture_attempts = F('_result_capture_attempts') + 1

            finally:
                self.obj.save()

    def update_from_async_result_and_save_if_change(self) -> None:
        has_changed = False

        async_result = self.obj.async_result

        new_meta = async_result.info

        if self.obj._task_meta != new_meta:
            self.obj._task_meta = new_meta
            has_changed = True

        new_state = async_result.state

        if self.obj.state != states.SUCCESS and new_state == states.SUCCESS:
            self.update_result(async_result)

        elif self.obj.state != new_state:
            self.obj.state = new_state
            has_changed = True

        if has_changed:
            self.obj.save()
