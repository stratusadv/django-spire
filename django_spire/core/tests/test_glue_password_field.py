from __future__ import annotations

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class GluePasswordFieldTemplateTestCase(SimpleTestCase):
    def render(self, **context: object) -> str:
        return render_to_string(
            'django_spire/glue/form/field/char/password_field.html',
            {'glue_field': 'form.password', **context},
        )

    def test_a_password_field_can_be_shown_as_it_is_typed(self) -> None:
        html = self.render()

        assert 'type="password"' in html
        assert ':type="passwordShown ? \'text\' : \'password\'"' in html
        assert 'data-password-toggle' in html
        assert 'class="input-group has-validation"' in html

    def test_a_password_field_can_leave_out_its_toggle(self) -> None:
        html = self.render(hide_toggle=True)

        assert 'type="password"' in html
        assert 'passwordShown' not in html
        assert 'data-password-toggle' not in html

    def test_a_fields_errors_show_whatever_wraps_its_input(self) -> None:
        assert ":class=\"{ 'd-block': field.hasErrors }\"" in self.render()
