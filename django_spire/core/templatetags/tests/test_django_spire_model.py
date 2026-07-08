from __future__ import annotations

import unittest

from django.contrib.auth.models import User
from django.template import Context, Template

from django_spire.core.templatetags.django_spire_model import model_app_label, model_name


class TestModelAppLabel(unittest.TestCase):
    def test_returns_app_label(self) -> None:
        class DummyModel:
            class _meta:  # noqa: N801
                app_label = 'my_app'

        result = model_app_label(DummyModel())

        assert result == 'my_app'

    def test_returns_correct_label_for_builtin_models(self) -> None:
        result = model_app_label(User())

        assert result == 'auth'

    def test_handles_custom_app_label(self) -> None:
        class CustomModel:
            class _meta:  # noqa: N801
                app_label = 'custom_app'

        result = model_app_label(CustomModel())

        assert result == 'custom_app'


class TestModelName(unittest.TestCase):
    def test_returns_model_name_lowercase(self) -> None:
        class DummyModel:
            class _meta:  # noqa: N801
                model_name = 'mymodel'

        result = model_name(DummyModel())

        assert result == 'mymodel'

    def test_returns_correct_name_for_builtin_models(self) -> None:
        result = model_name(User())

        assert result == 'user'

    def test_handles_uppercase_model_name(self) -> None:
        class CustomModel:
            class _meta:  # noqa: N801
                model_name = 'SomeModel'

        result = model_name(CustomModel())

        assert result == 'SomeModel'


class TestModelTemplateRendering(unittest.TestCase):
    def test_render_model_app_label_filter(self) -> None:
        template_code = """
            {% load django_spire_model %}

            {{ user | model_app_label }}
        """

        tmpl = Template(template_code)
        context = Context({'user': User()})
        rendered = tmpl.render(context)

        assert 'auth' in rendered

    def test_render_model_name_filter(self) -> None:
        template_code = """
            {% load django_spire_model %}

            {{ user | model_name }}
        """

        tmpl = Template(template_code)
        context = Context({'user': User()})
        rendered = tmpl.render(context)

        assert 'user' in rendered
