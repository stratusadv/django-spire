from __future__ import annotations

import json
import warnings

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.db import connections
from django.db.models import BooleanField, Case, QuerySet, Value, When

from django_spire.history.querysets import HistoryQuerySet
from django_spire.notification.choices import NotificationStatusChoices
from django_spire.notification.email.validators import (
    ALL_RECIPIENT_FIELDS,
    EmailListValidator,
    MAX_EMAIL_FIELD_LENGTH,
)
from django_spire.notification.querysets import NotificationContentObjectQuerySet

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.contrib.auth.models import User

    from django_spire.notification.email.models import EmailNotification


class EmailNotificationQuerySet(HistoryQuerySet, NotificationContentObjectQuerySet):
    def annotate_is_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).annotate(
            viewed=Case(
                When(views__user=user, then=Value(value=True)), default=Value(value=False), output_field=BooleanField()
            )
        )

    def bulk_create(self, objs: Iterable[EmailNotification], *args, **kwargs) -> list[EmailNotification]:
        obj_list = list(objs)

        for obj in obj_list:
            obj.sync_deprecated_to_email_address()
            obj.validate_recipients()

        created = super().bulk_create(obj_list, *args, **kwargs)

        for obj in created:
            obj._snapshot_recipient_fields()

        return created

    def bulk_update(self, objs: Iterable[EmailNotification], fields: Iterable[str], *args, **kwargs) -> int:
        obj_list = list(objs)
        field_names = list(fields)

        if ALL_RECIPIENT_FIELDS.intersection(field_names):
            for obj in obj_list:
                obj.sync_deprecated_to_email_address()
                obj.validate_recipients()

            if 'to' in field_names and 'to_email_address' not in field_names:
                field_names.append('to_email_address')
            elif 'to_email_address' in field_names and 'to' not in field_names:
                field_names.append('to')

        updated_count = super().bulk_update(obj_list, field_names, *args, **kwargs)

        for obj in obj_list:
            obj._snapshot_recipient_fields()

        return updated_count

    def by_to_email(self, email: str) -> QuerySet:
        if connections[self.db].features.supports_json_field_contains:
            return self.filter(to__contains=[email])

        return self.filter(to__icontains=json.dumps(email))

    def by_user(self, user: User) -> QuerySet:
        return self.filter(notification__user=user)

    def by_users(self, users: list[User]) -> QuerySet:
        return self.filter(notification__user__in=users)

    def exclude_viewed_by_user(self, user: User) -> QuerySet:
        return self.by_user(user=user).exclude(views__user=user)

    def is_sent(self) -> QuerySet:
        return self.filter(notification__status=NotificationStatusChoices.SENT)

    def update(self, **kwargs) -> int:
        if (
            'to_email_address' in kwargs
            and 'to' not in kwargs
            and not hasattr(kwargs['to_email_address'], 'resolve_expression')
        ):
            warnings.warn(
                'EmailNotification.to_email_address is deprecated; use EmailNotification.to=[...] instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            legacy_value = kwargs['to_email_address']
            kwargs['to'] = [legacy_value] if legacy_value else []

        self._validate_recipient_update_kwargs(kwargs)

        if 'to' in kwargs and not hasattr(kwargs['to'], 'resolve_expression'):
            to_value = kwargs['to']
            kwargs['to_email_address'] = to_value[0][:MAX_EMAIL_FIELD_LENGTH] if to_value else ''

        return super().update(**kwargs)

    @staticmethod
    def _validate_recipient_update_kwargs(kwargs: dict) -> None:
        errors: dict[str, list[ValidationError]] = {}

        validators = (
            ('to', EmailListValidator(allow_empty=False)),
            ('cc', EmailListValidator(allow_empty=True)),
            ('bcc', EmailListValidator(allow_empty=True)),
        )

        for field_name, validator in validators:
            if field_name not in kwargs or hasattr(kwargs[field_name], 'resolve_expression'):
                continue

            field_errors = EmailNotificationQuerySet._run_validator(kwargs[field_name], validator)

            if field_errors:
                errors[field_name] = field_errors

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def _run_validator(value: object, validator: EmailListValidator) -> list[ValidationError]:
        try:
            validator(value)
        except ValidationError as exc:
            return exc.error_list

        return []
