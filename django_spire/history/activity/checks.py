from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.core import checks

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.apps import AppConfig
    from django.db import models


ACTIVITY_MIDDLEWARE_PATH = 'django_spire.history.activity.middleware.ActivityUserMiddleware'
AUTHENTICATION_MIDDLEWARE_PATH = 'django.contrib.auth.middleware.AuthenticationMiddleware'


@checks.register(checks.Tags.models)
def check_activity_bulk_managers(
    app_configs: list[AppConfig] | None,
    **kwargs
) -> list[checks.CheckMessage]:
    _ = kwargs

    if app_configs is None:
        model_list = apps.get_models()
    else:
        model_list = [
            model
            for app_config in app_configs
            for model in app_config.get_models()
        ]

    warnings = []

    for model in model_list:
        if not issubclass(model, ActivityMixin):
            continue

        queryset_class = getattr(model._default_manager, '_queryset_class', None)

        if queryset_class is not None and issubclass(queryset_class, HistoryQuerySet):
            continue

        warnings.append(_bulk_manager_warning(model))

    return warnings


@checks.register(checks.Tags.compatibility)
def check_activity_middleware(
    app_configs: list[AppConfig] | None,
    **kwargs
) -> list[checks.CheckMessage]:
    _ = app_configs
    _ = kwargs

    middleware = list(getattr(settings, 'MIDDLEWARE', None) or [])

    if ACTIVITY_MIDDLEWARE_PATH not in middleware:
        warning = checks.Warning(
            'ActivityUserMiddleware is not in MIDDLEWARE, so no activity records '
            'will be created for requests.',
            hint=(
                f"Add '{ACTIVITY_MIDDLEWARE_PATH}' to MIDDLEWARE "
                f"after '{AUTHENTICATION_MIDDLEWARE_PATH}'."
            ),
            id='django_spire_history_activity.W001',
        )

        return [warning]

    if AUTHENTICATION_MIDDLEWARE_PATH not in middleware:
        return []

    activity_index = middleware.index(ACTIVITY_MIDDLEWARE_PATH)
    authentication_index = middleware.index(AUTHENTICATION_MIDDLEWARE_PATH)

    if activity_index < authentication_index:
        warning = checks.Warning(
            'ActivityUserMiddleware is listed before AuthenticationMiddleware, so '
            'request.user is not populated when the activity user is captured.',
            hint=(
                f"Move '{ACTIVITY_MIDDLEWARE_PATH}' after "
                f"'{AUTHENTICATION_MIDDLEWARE_PATH}' in MIDDLEWARE."
            ),
            id='django_spire_history_activity.W002',
        )

        return [warning]

    return []


def _bulk_manager_warning(model: type[models.Model]) -> checks.Warning:
    return checks.Warning(
        f'{model._meta.label} uses ActivityMixin but its default manager does not '
        'use a HistoryQuerySet, so bulk_create, bulk_update, and update will not '
        'create activity records, and queryset delete falls back to one insert '
        'per row.',
        hint=(
            "Derive the model's queryset from "
            "'django_spire.history.querysets.HistoryQuerySet' and assign it as "
            "the default manager: objects = MyQuerySet.as_manager()."
        ),
        obj=model,
        id='django_spire_history_activity.W003',
    )
