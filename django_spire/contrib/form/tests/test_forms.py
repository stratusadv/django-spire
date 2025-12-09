from __future__ import annotations

import pytest

from unittest.mock import MagicMock

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from django_spire.contrib.form.confirmation_forms import ConfirmationForm, DeleteConfirmationForm
from django_spire.contrib.form.utils import form_errors_as_list, show_form_errors


class TestConfirmationForm(TestCase):
    def test_confirmation_form_is_valid(self) -> None:
        form = ConfirmationForm(data={})

        assert form.is_valid() is True

    def test_confirmation_form_no_fields(self) -> None:
        form = ConfirmationForm()

        assert len(form.fields) == 0


class TestDeleteConfirmationForm(TestCase):
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
        with pytest.raises(ValueError, match='Passing an object to DeleteConfirmationForm is required'):
            DeleteConfirmationForm(data={})

    def test_init_with_obj(self) -> None:
        form = DeleteConfirmationForm(data={}, obj=self.obj)

        assert form.obj == self.obj

    def test_has_should_delete_field(self) -> None:
        form = DeleteConfirmationForm(data={}, obj=self.obj)

        assert 'should_delete' in form.fields

    def test_save_calls_set_deleted_by_default(self) -> None:
        form = DeleteConfirmationForm(data={'should_delete': True}, obj=self.obj)
        form.is_valid()

        del self.obj.add_activity

        form.save(user=self.user, verbs=('delete', 'deleted'))

        self.obj.set_deleted.assert_called_once()

    def test_save_calls_custom_delete_func(self) -> None:
        form = DeleteConfirmationForm(data={'should_delete': True}, obj=self.obj)
        form.is_valid()

        delete_func = MagicMock()
        del self.obj.add_activity

        form.save(user=self.user, verbs=('delete', 'deleted'), delete_func=delete_func)

        delete_func.assert_called_once()
        self.obj.set_deleted.assert_not_called()

    def test_save_calls_add_activity(self) -> None:
        form = DeleteConfirmationForm(data={'should_delete': True}, obj=self.obj)
        form.is_valid()

        form.save(user=self.user, verbs=('delete', 'deleted'))

        self.obj.add_activity.assert_called_once()
        call_kwargs = self.obj.add_activity.call_args[1]

        assert call_kwargs['user'] == self.user
        assert call_kwargs['verb'] == 'deleted'

    def test_save_calls_custom_activity_func(self) -> None:
        form = DeleteConfirmationForm(data={'should_delete': True}, obj=self.obj)
        form.is_valid()

        activity_func = MagicMock()

        form.save(user=self.user, verbs=('delete', 'deleted'), activity_func=activity_func)

        activity_func.assert_called_once()
        self.obj.add_activity.assert_not_called()

    def test_save_skips_activity_when_disabled(self) -> None:
        form = DeleteConfirmationForm(data={'should_delete': True}, obj=self.obj)
        form.is_valid()

        form.save(user=self.user, verbs=('delete', 'deleted'), auto_add_activity=False)

        self.obj.add_activity.assert_not_called()

    def test_should_delete_not_required(self) -> None:
        form = DeleteConfirmationForm(data={}, obj=self.obj)

        assert form.is_valid() is True


class TestFormErrorsAsList(TestCase):
    def test_empty_errors(self) -> None:
        form = MagicMock()
        form.errors = {}

        result = form_errors_as_list(form)

        assert result == []

    def test_field_error_with_messages(self) -> None:
        form = MagicMock()
        error = MagicMock()
        error.messages = ['This field is required.']
        del error.message_responses

        form.errors = MagicMock()
        form.errors.items.return_value = [('username', MagicMock(data=[error]))]

        result = form_errors_as_list(form)

        assert len(result) == 1
        assert 'Username' in result[0]
        assert 'This field is required.' in result[0]

    def test_non_field_error(self) -> None:
        form = MagicMock()
        error = MagicMock()
        error.messages = ['Form error message.']
        del error.message_responses

        form.errors = MagicMock()
        form.errors.items.return_value = [('__all__', MagicMock(data=[error]))]

        result = form_errors_as_list(form)

        assert len(result) == 1
        assert 'Form error message.' in result[0]
        assert '__all__' not in result[0]


class TestShowFormErrors(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_show_form_errors_adds_messages(self) -> None:
        request = self.factory.get('/')
        request.session = 'session'
        request._messages = FallbackStorage(request)

        form = MagicMock()
        error = MagicMock()
        error.messages = ['Test error']
        del error.message_responses

        form.errors = MagicMock()
        form.errors.items.return_value = [('field', MagicMock(data=[error]))]

        show_form_errors(request, form)

        messages_list = list(get_messages(request))

        assert len(messages_list) == 1
        assert 'Field' in str(messages_list[0])
        assert 'Test error' in str(messages_list[0])

    def test_show_form_errors_multiple_forms(self) -> None:
        request = self.factory.get('/')
        request.session = 'session'
        request._messages = FallbackStorage(request)

        error1 = MagicMock()
        error1.messages = ['Error 1']
        del error1.message_responses

        form1 = MagicMock()
        form1.errors = MagicMock()
        form1.errors.items.return_value = [('field1', MagicMock(data=[error1]))]

        error2 = MagicMock()
        error2.messages = ['Error 2']
        del error2.message_responses

        form2 = MagicMock()
        form2.errors = MagicMock()
        form2.errors.items.return_value = [('field2', MagicMock(data=[error2]))]

        show_form_errors(request, form1, form2)

        messages_list = list(get_messages(request))

        assert len(messages_list) == 2
