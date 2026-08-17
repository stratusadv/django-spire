from __future__ import annotations

import logging

from contextvars import ContextVar
from typing import Self, TYPE_CHECKING

from django.db import transaction
from django.db.models import QuerySet

from django_spire.history.activity.context import (
    get_current_user,
    get_delete_activity_entries,
    reset_delete_activity_collection,
    start_delete_activity_collection
)
from django_spire.history.activity.enums import ActivityVerb

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.contrib.auth.models import User
    from django.db import models

    from django_spire.history.activity.context import DeleteActivityEntry


_bulk_update_active: ContextVar[bool] = ContextVar('_bulk_update_active', default=False)

log = logging.getLogger(__name__)


class HistoryQuerySet(QuerySet):
    def active(self) -> Self:
        return self.filter(is_active=True, is_deleted=False)

    def inactive(self) -> Self:
        return self.filter(is_active=False, is_deleted=False)

    def deleted(self) -> Self:
        return self.filter(is_deleted=True)

    def not_deleted(self) -> Self:
        return self.filter(is_deleted=False)

    def bulk_create(
        self,
        objs: Iterable[models.Model],
        *,
        batch_size: int | None = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        update_fields: Iterable[str] | None = None,
        unique_fields: Iterable[str] | None = None,
    ) -> list[models.Model]:
        if not self._activity_enabled():
            return super().bulk_create(
                objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
            )

        with transaction.atomic(using=self.db):
            created = super().bulk_create(
                objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
            )

            if update_conflicts:
                log.warning(
                    'bulk_create with update_conflicts cannot distinguish created '
                    'rows from updated rows; no activity records were created.'
                )
            else:
                self._add_bulk_activity(created, ActivityVerb.CREATED)

        return created

    def bulk_update(
        self,
        objs: Iterable[models.Model],
        fields: Iterable[str],
        *args,
        **kwargs
    ) -> int:
        obj_list = list(objs)

        if not self._activity_enabled():
            return super().bulk_update(obj_list, fields, *args, **kwargs)

        field_names = set(fields)
        token = _bulk_update_active.set(True)

        try:
            with transaction.atomic(using=self.db):
                matched_pks = self._activity_matched_pks(obj_list)

                previously_deleted_pks = self._activity_previously_deleted_pks(
                    matched_pks,
                    field_names,
                )

                updated_count = super().bulk_update(obj_list, fields, *args, **kwargs)
                matched_objs = self._activity_matched_objs(obj_list, matched_pks)

                if 'is_deleted' in field_names:
                    deleted_objs = [
                        obj
                        for obj in matched_objs
                        if obj.is_deleted and obj.pk not in previously_deleted_pks
                    ]
                else:
                    deleted_objs = []

                deleted_obj_pks = {obj.pk for obj in deleted_objs}
                updated_objs = [obj for obj in matched_objs if obj.pk not in deleted_obj_pks]

                if updated_objs:
                    self._add_bulk_activity(updated_objs, ActivityVerb.UPDATED)

                if deleted_objs:
                    self._add_bulk_activity(deleted_objs, ActivityVerb.DELETED)
        finally:
            _bulk_update_active.reset(token)

        return updated_count

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        user = get_current_user()

        if user is None:
            return super().delete(*args, **kwargs)

        token = start_delete_activity_collection()

        try:
            with transaction.atomic(using=self.db):
                result = super().delete(*args, **kwargs)
                entries = get_delete_activity_entries() or []

                if entries:
                    self._add_bulk_delete_activity(entries, user)
        finally:
            reset_delete_activity_collection(token)

        return result

    def update(self, **kwargs) -> int:
        if _bulk_update_active.get() or not kwargs:
            return super().update(**kwargs)
        if not self._activity_enabled():
            return super().update(**kwargs)
        if self.query.is_sliced:
            return super().update(**kwargs)

        with transaction.atomic(using=self.db):
            pks = self._activity_update_target_pks()
            not_deleted_pks = self._activity_not_deleted_pks(pks, kwargs)
            updated_count = super().update(**kwargs)

            if updated_count < len(pks):
                log.warning(
                    'update() modified %d rows but snapshotted %d rows for '
                    'activity records; the audit trail may include rows the '
                    'update did not modify.',
                    updated_count,
                    len(pks),
                )

            if pks:
                instances = list(self.model._base_manager.using(self.db).filter(pk__in=pks))

                deleted_instances = [
                    obj
                    for obj in instances
                    if getattr(obj, 'is_deleted', False) and obj.pk in not_deleted_pks
                ]

                deleted_pks = {obj.pk for obj in deleted_instances}
                updated_instances = [obj for obj in instances if obj.pk not in deleted_pks]

                if updated_instances:
                    self._add_bulk_activity(updated_instances, ActivityVerb.UPDATED)

                if deleted_instances:
                    self._add_bulk_activity(deleted_instances, ActivityVerb.DELETED)

        return updated_count

    def _activity_enabled(self) -> bool:
        if not hasattr(self.model, 'add_activity'):
            return False

        return get_current_user() is not None

    def _activity_matched_objs(
        self,
        obj_list: list[models.Model],
        matched_pks: set
    ) -> list[models.Model]:
        matched_objs = []
        seen_pks = set()

        for obj in obj_list:
            if obj.pk not in matched_pks or obj.pk in seen_pks:
                continue

            seen_pks.add(obj.pk)
            matched_objs.append(obj)

        return matched_objs

    def _activity_matched_pks(self, obj_list: list[models.Model]) -> set:
        obj_pks = [obj.pk for obj in obj_list if obj.pk is not None]

        if not obj_pks:
            return set()

        return set(self.filter(pk__in=obj_pks).values_list('pk', flat=True))

    def _activity_not_deleted_pks(self, pks: list, update_kwargs: dict) -> set:
        if not pks:
            return set()
        if 'is_deleted' not in update_kwargs:
            return set()

        return set(
            self.model._base_manager
            .using(self.db)
            .filter(pk__in=pks, is_deleted=False)
            .values_list('pk', flat=True)
        )

    def _activity_previously_deleted_pks(self, matched_pks: set, field_names: set) -> set:
        if not matched_pks:
            return set()
        if 'is_deleted' not in field_names:
            return set()

        return set(
            self.model._base_manager
            .using(self.db)
            .filter(pk__in=matched_pks, is_deleted=True)
            .values_list('pk', flat=True)
        )

    def _activity_update_target_pks(self) -> list:
        from django_spire.history.activity.utils import BULK_ACTIVITY_COUNT_MAX  # noqa: PLC0415

        pk_queryset = self.order_by('pk')
        pk_queryset.query.select_for_update = False

        pks = list(pk_queryset.values_list('pk', flat=True)[:BULK_ACTIVITY_COUNT_MAX + 1])

        if len(pks) > BULK_ACTIVITY_COUNT_MAX:
            log.warning(
                'update() truncated "updated" activity records to the %d row cap; '
                'the audit trail for this operation is incomplete.',
                BULK_ACTIVITY_COUNT_MAX,
            )

            pks = pks[:BULK_ACTIVITY_COUNT_MAX]

        return pks

    def _add_bulk_activity(self, instances: Iterable[models.Model], verb: str) -> None:
        if not self._activity_enabled():
            return

        from django_spire.history.activity.utils import add_bulk_activity  # noqa: PLC0415

        add_bulk_activity(instances, get_current_user(), verb, using=self.db)

    def _add_bulk_delete_activity(self, entries: list[DeleteActivityEntry], user: User) -> None:
        user_queryset = user._meta.concrete_model._base_manager.using(self.db)

        if not user_queryset.filter(pk=user.pk).exists():
            log.warning(
                'delete() skipped %d "deleted" activity records because the '
                'acting user was removed by the same delete.',
                len(entries),
            )

            return

        from django_spire.history.activity.utils import add_bulk_delete_activity  # noqa: PLC0415

        add_bulk_delete_activity(entries, user, using=self.db)
