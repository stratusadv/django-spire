from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django_spire.contrib.form.confirmation_forms import ConfirmationForm


class TestConfirmationForm(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',  # noqa: S106
            first_name='Test',
            last_name='User'
        )
        self.obj = MagicMock()
        self.obj._meta.verbose_name = 'Test Object'
        self.obj.__str__ = MagicMock(return_value='Test Object Name')

    def test_init_raises_error_without_obj(self) -> None:
        with pytest.raises(ValueError, match='Passing an object to ConfirmationForm is required'):
            ConfirmationForm(data={})

    def test_init_with_obj(self) -> None:
        form = ConfirmationForm(data={}, obj=self.obj)

        assert form.obj == self.obj

    def test_has_should_confirm_field(self) -> None:
        form = ConfirmationForm(data={}, obj=self.obj)

        assert 'should_confirm' in form.fields

    def test_save_calls_add_activity(self) -> None:
        form = ConfirmationForm(data={'should_confirm': True}, obj=self.obj)
        form.is_valid()

        form.save(user=self.user, verbs=('delete', 'deleted'))

        self.obj.add_activity.assert_called_once()
        call_kwargs = self.obj.add_activity.call_args[1]

        assert call_kwargs['user'] == self.user
        assert call_kwargs['verb'] == 'deleted'

    def test_save_calls_custom_activity_func(self) -> None:
        form = ConfirmationForm(data={'should_confirm': True}, obj=self.obj)
        form.is_valid()

        activity_func = MagicMock()

        form.save(user=self.user, verbs=('delete', 'deleted'), activity_func=activity_func)

        activity_func.assert_called_once()
        self.obj.add_activity.assert_not_called()

    def test_save_skips_activity_when_disabled(self) -> None:
        form = ConfirmationForm(data={'should_confirm': True}, obj=self.obj)
        form.is_valid()

        form.save(user=self.user, verbs=('delete', 'deleted'), auto_add_activity=False)

        self.obj.add_activity.assert_not_called()

    def test_should_confirm_not_required(self) -> None:
        form = ConfirmationForm(data={}, obj=self.obj)

        assert form.is_valid() is True
