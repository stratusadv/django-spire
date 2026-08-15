from __future__ import annotations

from types import SimpleNamespace

from django.db import models
from django.test import SimpleTestCase, override_settings
from django.test.utils import isolate_apps

from django_spire.history.activity.checks import (
    ACTIVITY_MIDDLEWARE_PATH,
    AUTHENTICATION_MIDDLEWARE_PATH,
    check_activity_bulk_managers,
    check_activity_middleware
)
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.querysets import HistoryQuerySet


class TestActivityMiddlewareCheck(SimpleTestCase):
    def test_configured_middleware_passes(self) -> None:
        assert check_activity_middleware(None) == []

    def test_missing_middleware_warns(self) -> None:
        middleware = [AUTHENTICATION_MIDDLEWARE_PATH]

        with override_settings(MIDDLEWARE=middleware):
            messages = check_activity_middleware(None)

        assert len(messages) == 1
        assert messages[0].id == 'django_spire_history_activity.W001'

    def test_middleware_before_authentication_warns(self) -> None:
        middleware = [ACTIVITY_MIDDLEWARE_PATH, AUTHENTICATION_MIDDLEWARE_PATH]

        with override_settings(MIDDLEWARE=middleware):
            messages = check_activity_middleware(None)

        assert len(messages) == 1
        assert messages[0].id == 'django_spire_history_activity.W002'

    def test_middleware_after_authentication_passes(self) -> None:
        middleware = [AUTHENTICATION_MIDDLEWARE_PATH, ACTIVITY_MIDDLEWARE_PATH]

        with override_settings(MIDDLEWARE=middleware):
            messages = check_activity_middleware(None)

        assert messages == []


class TestActivityBulkManagerCheck(SimpleTestCase):
    def test_project_models_pass(self) -> None:
        assert check_activity_bulk_managers(None) == []

    @isolate_apps('django_spire.history.activity')
    def test_plain_manager_warns(self) -> None:
        class PlainManagerModel(ActivityMixin, models.Model):  # noqa: DJ008
            class Meta:
                app_label = 'django_spire_history_activity'

        app_config = SimpleNamespace(get_models=lambda: [PlainManagerModel])
        messages = check_activity_bulk_managers([app_config])

        assert len(messages) == 1
        assert messages[0].id == 'django_spire_history_activity.W003'
        assert messages[0].obj is PlainManagerModel

    @isolate_apps('django_spire.history.activity')
    def test_plain_queryset_manager_warns(self) -> None:
        class PlainQuerySetModel(ActivityMixin, models.Model):  # noqa: DJ008
            objects = models.QuerySet.as_manager()

            class Meta:
                app_label = 'django_spire_history_activity'

        app_config = SimpleNamespace(get_models=lambda: [PlainQuerySetModel])
        messages = check_activity_bulk_managers([app_config])

        assert len(messages) == 1
        assert messages[0].id == 'django_spire_history_activity.W003'

    @isolate_apps('django_spire.history.activity')
    def test_history_queryset_manager_passes(self) -> None:
        class HistoryManagerModel(ActivityMixin, models.Model):  # noqa: DJ008
            objects = HistoryQuerySet.as_manager()

            class Meta:
                app_label = 'django_spire_history_activity'

        app_config = SimpleNamespace(get_models=lambda: [HistoryManagerModel])

        assert check_activity_bulk_managers([app_config]) == []

    @isolate_apps('django_spire.history.activity')
    def test_model_without_mixin_is_ignored(self) -> None:
        class UnmixedModel(models.Model):  # noqa: DJ008
            class Meta:
                app_label = 'django_spire_history_activity'

        app_config = SimpleNamespace(get_models=lambda: [UnmixedModel])

        assert check_activity_bulk_managers([app_config]) == []
