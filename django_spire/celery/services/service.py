from __future__ import annotations

from celery import states
from django.db.models import F
from django.utils import timezone
from django.utils.timezone import now, get_current_timezone

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from sqlalchemy.exc import OperationalError, DatabaseError

if TYPE_CHECKING:
    from django_spire.celery.models import CeleryTask


class CeleryTaskService(BaseDjangoModelService['CeleryTask']):
    obj: CeleryTask

    def update_result(self) -> None:
        if self.obj.async_result.state == states.SUCCESS:
            try:
                self.obj.result = self.obj.async_result.get()

                self.obj.has_result = True

                date_done = self.obj.async_result.date_done

                if timezone.is_naive(date_done):
                    date_done_aware = timezone.make_aware(date_done, timezone.get_default_timezone())
                else:
                    date_done_aware = date_done

                self.obj.completed_datetime = date_done_aware
                self.obj.state = states.SUCCESS

                self.obj.save()
            except (OperationalError, DatabaseError):
                if self.obj._result_capture_attempts > 3:
                    self.obj.state = states.FAILURE
                else:
                    self.obj._result_capture_attempts = F('_result_capture_attempts') + 1

                self.obj.save()


    def update_from_async_result_and_save_if_change(self) -> None:
        current_state = self.obj.state
        new_state = self.obj.async_result.state

        if self.obj.state != states.SUCCESS and new_state == states.SUCCESS:
            self.update_result()
        elif current_state != new_state:
            self.obj.state = new_state
            self.obj.save()

