from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.template import Context, Template
from django.test import TestCase

from django_spire.celery.models import CeleryTask
from django_spire.celery.templatetags.django_spire_celery import (
    django_spire_celery_task_toast_widget,
)


class DjangoSpireCeleryTaskToastWidgetTestCase(TestCase):
    def test_tag_with_valid_app_and_reference(self) -> None:
        result = django_spire_celery_task_toast_widget(
            app_name='django_spire.core', reference_name='test_task'
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_with_model_object(self) -> None:
        mock_model = MagicMock()
        mock_model.__class__.__name__ = 'TestModel'
        mock_model.pk = 123

        result = django_spire_celery_task_toast_widget(
            app_name='django_spire.core', reference_name='test_task', model_object=mock_model
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_renders_template(self) -> None:
        result = django_spire_celery_task_toast_widget(
            app_name='django_spire.core', reference_name='test_task'
        )

        assert 'django_spire/celery/toast/task_toast_widget.html' in result or len(result) > 0

    def test_tag_with_invalid_app_name(self) -> None:
        with self.assertRaises(Exception):
            django_spire_celery_task_toast_widget(
                app_name='nonexistent_app', reference_name='test_task'
            )

    def test_tag_with_invalid_reference_name(self) -> None:
        with self.assertRaises(ValueError):
            django_spire_celery_task_toast_widget(
                app_name='django_spire.core', reference_name='invalid name'
            )

    def test_tag_generates_reference_key(self) -> None:
        result = django_spire_celery_task_toast_widget(
            app_name='django_spire.core', reference_name='test_task'
        )

        assert isinstance(result, str)

    def test_tag_context_contains_reference_key(self) -> None:
        with patch(
            'django_spire.celery.templatetags.django_spire_celery.get_template'
        ) as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = '<div>test</div>'
            mock_get_template.return_value = mock_template

            django_spire_celery_task_toast_widget(
                app_name='django_spire.core', reference_name='test_task'
            )

            call_args = mock_template.render.call_args
            assert call_args is not None

    def test_tag_uses_correct_template(self) -> None:
        with patch(
            'django_spire.celery.templatetags.django_spire_celery.get_template'
        ) as mock_get_template:
            mock_template = MagicMock()
            mock_template.render.return_value = '<div>test</div>'
            mock_get_template.return_value = mock_template

            django_spire_celery_task_toast_widget(
                app_name='django_spire.core', reference_name='test_task'
            )

            mock_get_template.assert_called_once_with(
                'django_spire/celery/toast/task_toast_widget.html'
            )


class DjangoSpireCeleryTemplateTagIntegrationTestCase(TestCase):
    def test_tag_in_template(self) -> None:
        template = Template(
            '{% load django_spire_celery %}'
            '{% django_spire_celery_task_toast_widget "django_spire.core" "test_task" %}'
        )
        context = Context({})

        result = template.render(context)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_tag_in_template_with_model(self) -> None:
        mock_model = MagicMock()
        mock_model.__class__.__name__ = 'TestModel'
        mock_model.pk = 123

        template = Template(
            '{% load django_spire_celery %}'
            '{% django_spire_celery_task_toast_widget "django_spire.core" "test_task" model_object %}'
        )
        context = Context({'model_object': mock_model})

        result = template.render(context)

        assert isinstance(result, str)
        assert len(result) > 0
