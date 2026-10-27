from __future__ import annotations

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class DeleteFormTemplateTestCase(SimpleTestCase):
    def test_delete_form_confirms_the_delete(self) -> None:
        html = render_to_string(
            'django_spire/form/delete_form.html',
            {'form_description': 'Are you sure you would like to delete group "Crew"?'},
        )

        assert 'method="post"' in html
        assert 'Are you sure you would like to delete group &quot;Crew&quot;?' in html
        assert '<input type="hidden" name="should_delete" value="true">' in html
