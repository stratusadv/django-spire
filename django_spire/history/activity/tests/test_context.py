from __future__ import annotations

import pytest

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser, User
from django.db import models
from django.test import RequestFactory

from django_spire.history.activity.context import (
    get_current_user,
    reset_current_user,
    set_current_user
)
from django_spire.history.activity.middleware import ActivityUserMiddleware
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.activity.signals import (
    create_activity_on_delete,
    create_activity_on_save
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from django.http import HttpRequest


@pytest.fixture(autouse=True)
def _clear_context() -> Generator[None]:
    yield
    set_current_user(None)


@pytest.fixture
def factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def user() -> User:
    return User(pk=1, first_name='Test', last_name='User')


def _make_instance(has_mixin: bool = True) -> MagicMock:
    instance = MagicMock(spec=ActivityMixin) if has_mixin else MagicMock(spec=models.Model)
    instance._meta = MagicMock()
    instance._meta.verbose_name = 'test object'
    instance.__str__ = MagicMock(return_value='Test Object')

    return instance


class TestContext:
    def test_default_is_none(self) -> None:
        assert get_current_user() is None

    def test_get_returns_set_user(self, user: User) -> None:
        set_current_user(user)

        assert get_current_user() == user

    def test_set_none_clears_user(self, user: User) -> None:
        set_current_user(user)
        set_current_user(None)

        assert get_current_user() is None

    def test_reset_restores_previous_user(self, user: User) -> None:
        set_current_user(user)

        other_user = User(pk=2, first_name='Other', last_name='User')
        token = set_current_user(other_user)

        reset_current_user(token)

        assert get_current_user() == user

    def test_reset_restores_default(self, user: User) -> None:
        token = set_current_user(user)

        reset_current_user(token)

        assert get_current_user() is None


class TestMiddleware:
    def test_authenticated_user_is_set(self, factory: RequestFactory, user: User) -> None:
        captured_user = None

        def _mock_response(_request: HttpRequest) -> MagicMock:
            nonlocal captured_user
            captured_user = get_current_user()

            return MagicMock()

        request = factory.get('/')
        request.user = user

        middleware = ActivityUserMiddleware(_mock_response)
        middleware(request)

        assert captured_user == user

    def test_anonymous_user_is_not_set(self, factory: RequestFactory) -> None:
        captured_user = 'sentinel'

        def _mock_response(_request: HttpRequest) -> MagicMock:
            nonlocal captured_user
            captured_user = get_current_user()

            return MagicMock()

        request = factory.get('/')
        request.user = AnonymousUser()

        middleware = ActivityUserMiddleware(_mock_response)
        middleware(request)

        assert captured_user is None

    def test_user_cleared_after_response(self, factory: RequestFactory, user: User) -> None:
        request = factory.get('/')
        request.user = user

        middleware = ActivityUserMiddleware(lambda _request: MagicMock())
        middleware(request)

        assert get_current_user() is None

    def test_user_cleared_after_exception(self, factory: RequestFactory, user: User) -> None:
        def _mock_response(_request: HttpRequest) -> MagicMock:
            raise ValueError

        request = factory.get('/')
        request.user = user

        middleware = ActivityUserMiddleware(_mock_response)

        with pytest.raises(ValueError):
            middleware(request)

        assert get_current_user() is None

    def test_no_user_attribute_on_request(self) -> None:
        captured_user = 'sentinel'

        def _mock_response(_request: HttpRequest) -> MagicMock:
            nonlocal captured_user
            captured_user = get_current_user()

            return MagicMock()

        request = MagicMock(spec=[])

        middleware = ActivityUserMiddleware(_mock_response)
        middleware(request)

        assert captured_user is None


class TestSignal:
    def test_activity_created_on_insert(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        instance.add_activity.assert_called_once()
        call_kwargs = instance.add_activity.call_args.kwargs

        assert call_kwargs['user'] == user
        assert call_kwargs['verb'] == 'created'
        assert 'created' in call_kwargs['information']

    def test_activity_created_on_update(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=False)

        instance.add_activity.assert_called_once()
        call_kwargs = instance.add_activity.call_args.kwargs

        assert call_kwargs['user'] == user
        assert call_kwargs['verb'] == 'updated'
        assert 'updated' in call_kwargs['information']

    def test_no_activity_without_user(self) -> None:
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        instance.add_activity.assert_not_called()

    def test_no_activity_without_mixin(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance(has_mixin=False)

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        assert not hasattr(instance, 'add_activity')

    def test_information_contains_user_full_name(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        call_kwargs = instance.add_activity.call_args.kwargs

        assert 'Test User' in call_kwargs['information']

    def test_information_contains_verbose_name(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        call_kwargs = instance.add_activity.call_args.kwargs

        assert 'test object' in call_kwargs['information']

    def test_information_contains_instance_str(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        call_kwargs = instance.add_activity.call_args.kwargs

        assert 'Test Object' in call_kwargs['information']

    def test_no_activity_on_raw_save(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_save(sender=type(instance), instance=instance, created=True, raw=True)

        instance.add_activity.assert_not_called()

    def test_no_recursion(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()
        nested_calls = []

        def _side_effect(**kwargs) -> None:
            nested_instance = _make_instance()
            create_activity_on_save(sender=type(nested_instance), instance=nested_instance, created=True)
            nested_calls.append(nested_instance)

        instance.add_activity.side_effect = _side_effect

        create_activity_on_save(sender=type(instance), instance=instance, created=True)

        instance.add_activity.assert_called_once()
        nested_calls[0].add_activity.assert_not_called()


class TestDeleteSignal:
    def test_activity_created_on_delete(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance()

        create_activity_on_delete(sender=type(instance), instance=instance)

        instance.add_activity.assert_called_once()
        call_kwargs = instance.add_activity.call_args.kwargs

        assert call_kwargs['user'] == user
        assert call_kwargs['verb'] == 'deleted'
        assert 'deleted' in call_kwargs['information']

    def test_no_activity_without_user(self) -> None:
        instance = _make_instance()

        create_activity_on_delete(sender=type(instance), instance=instance)

        instance.add_activity.assert_not_called()

    def test_no_activity_without_mixin(self, user: User) -> None:
        set_current_user(user)
        instance = _make_instance(has_mixin=False)

        create_activity_on_delete(sender=type(instance), instance=instance)

        assert not hasattr(instance, 'add_activity')
