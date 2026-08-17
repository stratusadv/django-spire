from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.db.models.signals import m2m_changed, post_delete, post_save

from django_spire.history.activity.context import (
    ACTIVITY_VERB_ATTRIBUTE,
    get_current_user,
    get_delete_activity_entries
)
from django_spire.history.activity.enums import ActivityM2mAction, ActivityVerb
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.activity.utils import (
    actor_name,
    add_activity,
    build_activity_information
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.db import models


ACTIVITY_M2M_ACTIONS_HANDLED = frozenset({
    ActivityM2mAction.POST_ADD,
    ActivityM2mAction.POST_CLEAR,
    ActivityM2mAction.POST_REMOVE,
    ActivityM2mAction.PRE_CLEAR,
    ActivityM2mAction.PRE_REMOVE,
})

ACTIVITY_M2M_CLEARED_STATE_ATTRIBUTE = '_activity_m2m_cleared_state'
ACTIVITY_M2M_NAMED_COUNT_MAX = 10
ACTIVITY_M2M_PRESENT_PK_SET_ATTRIBUTE = '_activity_m2m_present_pk_set'


def connect_activity_signals() -> None:
    for model in apps.get_models():
        if not issubclass(model, ActivityMixin):
            continue

        label = model._meta.label_lower

        post_save.connect(
            create_activity_on_save,
            sender=model,
            dispatch_uid=f'django_spire_activity_post_save.{label}',
        )

        post_delete.connect(
            create_activity_on_delete,
            sender=model,
            dispatch_uid=f'django_spire_activity_post_delete.{label}',
        )

        for field in model._meta.many_to_many:
            _connect_m2m(field.remote_field.through)

        for relation in model._meta.related_objects:
            if relation.many_to_many:
                _connect_m2m(relation.through)


def create_activity_on_delete(
    sender: type[models.Model],
    instance: models.Model,
    **kwargs
) -> None:
    _ = sender
    _ = kwargs

    if not isinstance(instance, ActivityMixin):
        return

    user = get_current_user()

    if not user:
        return

    if _is_same_row(instance, user):
        return

    entries = get_delete_activity_entries()

    if entries is not None:
        entry = (
            instance._meta.concrete_model,
            instance.pk,
            build_activity_information(instance, user, ActivityVerb.DELETED),
        )

        entries.append(entry)

        return

    add_activity(instance, user, ActivityVerb.DELETED)


def create_activity_on_m2m_change(
    sender: type[models.Model],
    instance: models.Model,
    action: str,
    model: type[models.Model],
    pk_set: set | None,
    *,
    reverse: bool = False,
    **kwargs
) -> None:
    _ = kwargs

    if action not in ACTIVITY_M2M_ACTIONS_HANDLED:
        return

    if not isinstance(instance, ActivityMixin):
        return

    user = get_current_user()

    if not user:
        return

    if action == ActivityM2mAction.PRE_CLEAR:
        cleared_state = _m2m_cleared_state(sender, instance, model, reverse)
        instance.__dict__[ACTIVITY_M2M_CLEARED_STATE_ATTRIBUTE] = cleared_state
        return

    if action == ActivityM2mAction.PRE_REMOVE:
        present_pk_set = _m2m_present_pk_set(sender, instance, model, pk_set, reverse)
        instance.__dict__[ACTIVITY_M2M_PRESENT_PK_SET_ATTRIBUTE] = present_pk_set
        return

    count, named_pks = _m2m_change_state(action, instance, pk_set)

    if count == 0:
        return

    if action == ActivityM2mAction.POST_ADD:
        verb = ActivityVerb.ADDED
        preposition = 'to'
    else:
        verb = ActivityVerb.REMOVED
        preposition = 'from'

    related_name = (
        model._meta.verbose_name
        if count == 1
        else model._meta.verbose_name_plural
    )

    names = _m2m_related_names(model, named_pks)

    information = _m2m_information(
        user=user,
        verb=verb,
        count=count,
        related_name=related_name,
        preposition=preposition,
        instance=instance,
        names=names,
    )

    instance.add_activity(user=user, verb=verb, information=information)


def create_activity_on_save(
    sender: type[models.Model],
    instance: models.Model,
    created: bool,
    raw: bool = False,
    **kwargs
) -> None:
    _ = sender
    _ = kwargs

    if not isinstance(instance, ActivityMixin):
        return

    verb_override = instance.__dict__.pop(ACTIVITY_VERB_ATTRIBUTE, None)

    if raw:
        return

    user = get_current_user()

    if not user:
        return

    if verb_override is not None:
        verb = verb_override
    elif created:
        verb = ActivityVerb.CREATED
    else:
        verb = ActivityVerb.UPDATED

    add_activity(instance, user, verb)


def _connect_m2m(through: type[models.Model]) -> None:
    label = through._meta.label_lower

    m2m_changed.connect(
        create_activity_on_m2m_change,
        sender=through,
        dispatch_uid=f'django_spire_activity_m2m_changed.{label}',
    )


def _is_same_row(instance: models.Model, user: User) -> bool:
    if instance.pk != user.pk:
        return False

    return instance._meta.concrete_model is user._meta.concrete_model


def _m2m_change_state(
    action: str,
    instance: models.Model,
    pk_set: set | None
) -> tuple[int, list]:
    if action == ActivityM2mAction.POST_CLEAR:
        return instance.__dict__.pop(ACTIVITY_M2M_CLEARED_STATE_ATTRIBUTE, (0, []))

    if action == ActivityM2mAction.POST_REMOVE:
        present_pk_set = instance.__dict__.pop(ACTIVITY_M2M_PRESENT_PK_SET_ATTRIBUTE, None)

        if present_pk_set is not None:
            named_pks = sorted(present_pk_set)[:ACTIVITY_M2M_NAMED_COUNT_MAX]
            return len(present_pk_set), named_pks

    if not pk_set:
        return 0, []

    named_pks = sorted(pk_set)[:ACTIVITY_M2M_NAMED_COUNT_MAX]
    return len(pk_set), named_pks


def _m2m_cleared_state(
    sender: type[models.Model],
    instance: models.Model,
    model: type[models.Model],
    reverse: bool
) -> tuple[int, list]:
    source_field, target_field = _m2m_relation_fields(sender, instance, model, reverse)

    if source_field is None:
        return 0, []

    source_filter = {source_field.attname: instance.pk}
    through_queryset = sender._default_manager.filter(**source_filter)
    count = through_queryset.count()

    if target_field is None:
        return count, []

    named_pks = list(
        through_queryset
        .order_by(target_field.attname)
        .values_list(target_field.attname, flat=True)[:ACTIVITY_M2M_NAMED_COUNT_MAX]
    )

    return count, named_pks


def _m2m_information(
    *,
    user: User,
    verb: str,
    count: int,
    related_name: str,
    preposition: str,
    instance: models.Model,
    names: list[str],
) -> str:
    base = (
        f'{actor_name(user)} {verb} {count} {related_name} '
        f'{preposition} {instance._meta.verbose_name} "{instance}"'
    )

    if not names:
        return f'{base}.'

    named = ', '.join(names)

    if count > len(names):
        return f'{base} ({named}, and {count - len(names)} more).'

    return f'{base} ({named}).'


def _m2m_present_pk_set(
    sender: type[models.Model],
    instance: models.Model,
    model: type[models.Model],
    pk_set: set | None,
    reverse: bool
) -> set:
    if not pk_set:
        return set()

    source_field, target_field = _m2m_relation_fields(sender, instance, model, reverse)

    if source_field is None or target_field is None:
        return set(pk_set)

    source_filter = {
        source_field.attname: instance.pk,
        f'{target_field.attname}__in': pk_set,
    }

    return set(
        sender._default_manager
        .filter(**source_filter)
        .values_list(target_field.attname, flat=True)
    )


def _m2m_related_names(model: type[models.Model], named_pks: list) -> list[str]:
    if not named_pks:
        return []

    related_objects = model._default_manager.filter(pk__in=named_pks)

    return sorted(str(related_object) for related_object in related_objects)


def _m2m_relation_fields(
    sender: type[models.Model],
    instance: models.Model,
    model: type[models.Model],
    reverse: bool
) -> tuple[models.Field | None, models.Field | None]:
    instance_fields = [
        field
        for field in sender._meta.concrete_fields
        if field.is_relation and isinstance(instance, field.related_model)
    ]

    if len(instance_fields) >= 2:
        source_field = instance_fields[1] if reverse else instance_fields[0]
        target_field = instance_fields[0] if reverse else instance_fields[1]

        return source_field, target_field

    source_field = instance_fields[0] if instance_fields else None
    target_field = None

    for field in sender._meta.concrete_fields:
        if not field.is_relation:
            continue

        if field is source_field:
            continue

        if target_field is None and issubclass(model, field.related_model):
            target_field = field

    return source_field, target_field
