from __future__ import annotations

import warnings

import pytest

from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.form.confirmation_forms import (
    ConfirmationForm,
    DeleteConfirmationForm
)
from django_spire.history.activity.context import activity_user
from django_spire.history.activity.models import Activity

from test_project.app.task.models import Task


class TestConfirmationFormSave(TestCase):
    def setUp(self) -> None:
        self.task = Task.objects.create(name='One')

    def test_save_calls_confirmation_func(self) -> None:
        calls = []

        form = ConfirmationForm({'should_confirm': True}, obj=self.task)
        form.is_valid()
        form.save(confirmation_func=lambda: calls.append('confirmed'))

        assert calls == ['confirmed']

    def test_save_without_removed_arguments_does_not_warn(self) -> None:
        form = ConfirmationForm({'should_confirm': True}, obj=self.task)
        form.is_valid()

        with warnings.catch_warnings():
            warnings.simplefilter('error')
            form.save()

    def test_save_with_removed_arguments_warns(self) -> None:
        form = ConfirmationForm({'should_confirm': True}, obj=self.task)
        form.is_valid()

        verbs = ('confirm', 'confirmed')

        with pytest.warns(DeprecationWarning, match='verbs and auto_add_activity'):
            form.save(None, verbs)


class TestDeleteConfirmationFormSave(TestCase):
    def setUp(self) -> None:
        self.task = Task.objects.create(name='One')

    def test_save_defaults_to_set_deleted(self) -> None:
        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()
        form.save()

        self.task.refresh_from_db()
        assert self.task.is_deleted is True

    def test_save_calls_delete_func(self) -> None:
        calls = []

        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()
        form.save(delete_func=lambda: calls.append('deleted'))

        assert calls == ['deleted']

        self.task.refresh_from_db()
        assert self.task.is_deleted is False

    def test_save_accepts_legacy_positional_arguments_with_warning(self) -> None:
        calls = []

        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()

        verbs = ('delete', 'deleted')

        with pytest.warns(DeprecationWarning, match='verbs and auto_add_activity'):
            form.save(None, verbs, lambda: calls.append('deleted'))

        assert calls == ['deleted']

    def test_save_invokes_legacy_activity_func_with_warning(self) -> None:
        calls = []

        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()

        with pytest.warns(DeprecationWarning, match='activity_func argument is deprecated'):
            form.save(activity_func=lambda: calls.append('activity'), auto_add_activity=False)

        assert calls == ['activity']

        self.task.refresh_from_db()
        assert self.task.is_deleted is True

    def test_save_returns_none(self) -> None:
        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()

        assert form.save() is None

    def test_save_deletes_even_when_should_delete_is_unchecked(self) -> None:
        form = DeleteConfirmationForm({}, obj=self.task)
        form.is_valid()
        form.save()

        self.task.refresh_from_db()

        assert form.cleaned_data['should_delete'] is False
        assert self.task.is_deleted is True

    def test_auto_add_activity_alone_warns(self) -> None:
        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()

        with pytest.warns(DeprecationWarning, match='auto_add_activity'):
            form.save(auto_add_activity=True)


class TestConfirmationFormValidation(TestCase):
    def test_confirmation_form_requires_an_object(self) -> None:
        with pytest.raises(ValueError, match='required'):
            ConfirmationForm({'should_confirm': True})

    def test_delete_confirmation_form_requires_an_object(self) -> None:
        with pytest.raises(ValueError, match='required'):
            DeleteConfirmationForm({'should_delete': True})

    def test_confirmation_form_is_valid_without_data(self) -> None:
        task = Task.objects.create(name='One')
        form = ConfirmationForm({}, obj=task)

        assert form.is_valid() is True
        assert form.cleaned_data['should_confirm'] is False


class TestConfirmationFormActivity(TestCase):
    def setUp(self) -> None:
        self.user = AuthUser.objects.create_user(
            username='confirmactor',
            first_name='Confirm',
            last_name='Actor',
        )

        self.task = Task.objects.create(name='One')

    def test_delete_form_logs_exactly_one_deleted_activity(self) -> None:
        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()

        with activity_user(self.user):
            form.save()

        assert Activity.objects.filter(verb='deleted').count() == 1
        assert Activity.objects.filter(verb='updated').count() == 0

    def test_confirmation_form_logs_nothing_on_its_own(self) -> None:
        form = ConfirmationForm({'should_confirm': True}, obj=self.task)
        form.is_valid()

        with activity_user(self.user):
            form.save()

        assert Activity.objects.count() == 0

    def test_delete_form_without_an_ambient_user_logs_nothing(self) -> None:
        form = DeleteConfirmationForm({'should_delete': True}, obj=self.task)
        form.is_valid()
        form.save()

        self.task.refresh_from_db()

        assert self.task.is_deleted is True
        assert Activity.objects.count() == 0
