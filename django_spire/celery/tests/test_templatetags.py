from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.template import Context, Template
from django.test import TestCase, override_settings

from django_spire.celery.manager import BaseCeleryTaskManager
from django_spire.celery.templatetags.django_spire_celery import (
    django_spire_celery_task_toast_widget,
    django_spire_celery_task_item_block,
)


class TestCeleryTaskManager(BaseCeleryTaskManager):
    task_name = 'test_task'
    display_name = 'Test Task'


class TestCeleryTaskManagerWithModel(BaseCeleryTaskManager):
    task_name = 'test_task_with_model'
    display_name = 'Test Task With Model'


class DjangoSpireCeleryTaskToastWidgetTestCase(TestCase):
    def test_tag_with_valid_manager(self) -> None:
        manager = TestCeleryTaskManager()
        result = django_spire_celery_task_toast_widget([manager])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_model_object_manager(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = TestCeleryTaskManagerWithModel(model_object=mock_model)
        result = django_spire_celery_task_toast_widget([manager])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_multiple_managers(self) -> None:
        manager1 = TestCeleryTaskManager()
        mock_model = MagicMock()
        mock_model.pk = 123
        manager2 = TestCeleryTaskManagerWithModel(model_object=mock_model)

        result = django_spire_celery_task_toast_widget([manager1, manager2])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_empty_list(self) -> None:
        result = django_spire_celery_task_toast_widget([])
        assert result is None

    def test_tag_with_non_list_returns_none(self) -> None:
        result = django_spire_celery_task_toast_widget('not a list')
        assert result is None

    def test_tag_with_non_manager_in_list_returns_none(self) -> None:
        result = django_spire_celery_task_toast_widget(['not a manager'])
        assert result is None

    @patch('django_spire.celery.templatetags.django_spire_celery.get_template')
    def test_tag_renders_correct_template(self, mock_get_template) -> None:
        mock_template = MagicMock()
        mock_template.render.return_value = '<div>test</div>'
        mock_get_template.return_value = mock_template

        manager = TestCeleryTaskManager()
        django_spire_celery_task_toast_widget([manager])

        mock_get_template.assert_called_once_with('django_spire/celery/toast/task_toast_widget.html')

    @patch('django_spire.celery.templatetags.django_spire_celery.get_template')
    def test_tag_passes_key_pairs_to_context(self, mock_get_template) -> None:
        mock_template = MagicMock()
        mock_template.render.return_value = '<div>test</div>'
        mock_get_template.return_value = mock_template

        manager = TestCeleryTaskManager()
        django_spire_celery_task_toast_widget([manager])

        call_args = mock_template.render.call_args[0]
        call_kwargs = mock_template.render.call_args[1]
        context = call_args[0] if call_args else call_kwargs
        assert 'django_spire_celery_task_key_pairs' in context
        assert isinstance(context['django_spire_celery_task_key_pairs'], str)


class DjangoSpireCeleryTaskItemBlockTestCase(TestCase):
    def test_tag_with_valid_manager(self) -> None:
        manager = TestCeleryTaskManager()
        result = django_spire_celery_task_item_block([manager])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_model_object_manager(self) -> None:
        mock_model = MagicMock()
        mock_model.pk = 123

        manager = TestCeleryTaskManagerWithModel(model_object=mock_model)
        result = django_spire_celery_task_item_block([manager])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_multiple_managers(self) -> None:
        manager1 = TestCeleryTaskManager()
        mock_model = MagicMock()
        mock_model.pk = 123
        manager2 = TestCeleryTaskManagerWithModel(model_object=mock_model)

        result = django_spire_celery_task_item_block([manager1, manager2])

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_empty_list(self) -> None:
        result = django_spire_celery_task_item_block([])
        assert result is None

    def test_tag_with_non_list_returns_none(self) -> None:
        result = django_spire_celery_task_item_block('not a list')
        assert result is None

    @patch('django_spire.celery.templatetags.django_spire_celery.get_template')
    def test_tag_renders_correct_template(self, mock_get_template) -> None:
        mock_template = MagicMock()
        mock_template.render.return_value = '<div>test</div>'
        mock_get_template.return_value = mock_template

        manager = TestCeleryTaskManager()
        django_spire_celery_task_item_block([manager])

        mock_get_template.assert_called_once_with('django_spire/celery/item/task_item_block.html')

    @patch('django_spire.celery.templatetags.django_spire_celery.get_template')
    def test_tag_passes_key_pairs_to_context(self, mock_get_template) -> None:
        mock_template = MagicMock()
        mock_template.render.return_value = '<div>test</div>'
        mock_get_template.return_value = mock_template

        manager = TestCeleryTaskManager()
        django_spire_celery_task_item_block([manager])

        call_args = mock_template.render.call_args[0]
        call_kwargs = mock_template.render.call_args[1]
        context = call_args[0] if call_args else call_kwargs
        assert 'django_spire_celery_task_key_pairs' in context
        assert isinstance(context['django_spire_celery_task_key_pairs'], str)


class DjangoSpireCeleryTemplateTagIntegrationTestCase(TestCase):
    def test_toast_widget_tag_in_template(self) -> None:
        template = Template(
            '{% load django_spire_celery %}'
            '{% django_spire_celery_task_toast_widget managers %}'
        )
        manager = TestCeleryTaskManager()
        context = Context({'managers': [manager]})

        result = template.render(context)

        assert isinstance(result, str)

    def test_item_block_tag_in_template(self) -> None:
        template = Template(
            '{% load django_spire_celery %}'
            '{% django_spire_celery_task_item_block managers %}'
        )
        manager = TestCeleryTaskManager()
        context = Context({'managers': [manager]})

        result = template.render(context)

        assert isinstance(result, str)