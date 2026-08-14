from __future__ import annotations

from unittest.mock import patch

from django.template import RequestContext, Template
from django.test import RequestFactory


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_define_modal(mock_render_to_string) -> None:
    mock_render_to_string.return_value = '<div>Modal content</div>'
    request = RequestFactory().get('/')
    template = Template("""
        {% load django_spire_modal %}
        {% define_modal id='task-form' template='task/form.html' %}
    """)

    rendered = template.render(RequestContext(request, {}))

    assert 'id="task-form"' in rendered
    assert 'data-spire-modal' in rendered
    assert '<div>Modal content</div>' in rendered
    mock_render_to_string.assert_called_once()
