from __future__ import annotations

import re
from unittest.mock import patch

from django.template import RequestContext, Template
from django.test import RequestFactory

from django_spire.core.templatetags.django_spire_modal import modal_id


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


def test_modal_id_is_deterministic_for_the_same_template_path() -> None:
    first = modal_id('partner/agreement/company_rep/modal/content/company_rep_form_modal_content.html')
    second = modal_id('partner/agreement/company_rep/modal/content/company_rep_form_modal_content.html')

    assert first == second


def test_modal_id_differs_across_template_paths() -> None:
    assert modal_id('task/form.html') != modal_id('task/delete_confirm.html')


def test_modal_id_only_contains_id_safe_characters() -> None:
    generated = modal_id('partner/agreement/company_rep/modal/content/company_rep_form_modal_content.html')

    assert re.fullmatch(r'[a-zA-Z0-9_-]+', generated)


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_static_modal_outputs_only_the_deterministic_id(mock_render_to_string) -> None:
    mock_render_to_string.return_value = '<div>Modal content</div>'
    request = RequestFactory().get('/')
    template = Template("""
        {% load django_spire_modal %}
        {% static_modal template='task/form.html' as captured_id %}{{ captured_id }}
    """)

    rendered = template.render(RequestContext(request, {}))

    # No <template> element at the call site -- it's queued for
    # render_static_modals to drain elsewhere -- and the captured id must
    # match what the modal_id filter computes independently.
    assert 'data-spire-modal' not in rendered
    assert rendered.strip() == modal_id('task/form.html')


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_render_static_modals_drains_queued_elements(mock_render_to_string) -> None:
    mock_render_to_string.return_value = '<div>Modal content</div>'
    request = RequestFactory().get('/')
    template = Template("""
        {% load django_spire_modal %}
        {% static_modal template='task/form.html' as modal_id %}
        <a data-trigger-for="{{ modal_id }}"></a>
        {% render_static_modals %}
    """)

    rendered = template.render(RequestContext(request, {}))

    trigger_id_match = re.search(r'data-trigger-for="(modal-[a-zA-Z0-9_-]+)"', rendered)
    element_id_match = re.search(r'<template id="(modal-[a-zA-Z0-9_-]+)" data-spire-modal>', rendered)

    assert trigger_id_match is not None
    assert element_id_match is not None
    assert trigger_id_match.group(1) == element_id_match.group(1)
    assert '<div>Modal content</div>' in rendered


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_render_static_modals_is_a_noop_with_nothing_queued(mock_render_to_string) -> None:
    request = RequestFactory().get('/')
    template = Template("""
        {% load django_spire_modal %}
        {% render_static_modals %}
    """)

    rendered = template.render(RequestContext(request, {}))

    assert 'data-spire-modal' not in rendered
    mock_render_to_string.assert_not_called()


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_static_modal_dedupes_repeated_calls_for_the_same_template(mock_render_to_string) -> None:
    """Calling static_modal with the same template path more than once (e.g.
    once per row of a list, for a shared edit-form modal) must only queue a
    single <template> element -- not one per row.
    """
    mock_render_to_string.return_value = '<div>Modal content</div>'
    request = RequestFactory().get('/')
    template = Template("""
        {% load django_spire_modal %}
        {% static_modal template='task/form.html' as first_id %}
        {% static_modal template='task/form.html' as second_id %}
        {{ first_id }}|{{ second_id }}
        {% render_static_modals %}
    """)

    rendered = template.render(RequestContext(request, {}))

    first_id, second_id = rendered.split('|')[0].strip(), rendered.split('|')[1].split()[0]
    assert first_id == second_id == modal_id('task/form.html')

    element_ids = re.findall(r'<template id="(modal-[a-zA-Z0-9_-]+)" data-spire-modal>', rendered)
    assert len(element_ids) == 1
    mock_render_to_string.assert_called_once()


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_static_modal_ids_are_unique_across_different_templates(mock_render_to_string) -> None:
    mock_render_to_string.return_value = '<div>Modal content</div>'
    request = RequestFactory().get('/')
    template = Template("""
        {% load django_spire_modal %}
        {% static_modal template='task/form.html' as first_id %}
        {% static_modal template='task/delete_confirm.html' as second_id %}
        {% render_static_modals %}
    """)

    rendered = template.render(RequestContext(request, {}))

    element_ids = re.findall(r'<template id="(modal-[a-zA-Z0-9_-]+)" data-spire-modal>', rendered)
    assert len(element_ids) == 2
    assert element_ids[0] != element_ids[1]

    # A second drain in the same request must not re-render stale elements.
    second_render = Template("""
        {% load django_spire_modal %}
        {% render_static_modals %}
    """).render(RequestContext(request, {}))

    assert 'data-spire-modal' not in second_render


@patch('django_spire.core.templatetags.django_spire_modal.render_to_string')
def test_static_modal_id_is_stable_across_separate_renders(mock_render_to_string) -> None:
    """The whole point: a fragment response rendered later (e.g. a Glue.view
    refresh of a list partial that includes its own {% render_static_modals %})
    must produce the exact same id as the original full-page render did --
    it's a pure function of the template path, not request-scoped state.
    """
    mock_render_to_string.return_value = '<div>Modal content</div>'

    first_pass = Template("""
        {% load django_spire_modal %}
        {% static_modal template='task/form.html' as modal_id %}{{ modal_id }}|{% render_static_modals %}
    """).render(RequestContext(RequestFactory().get('/'), {}))
    first_id = first_pass.split('|')[0].strip()

    second_pass = Template("""
        {% load django_spire_modal %}
        {% static_modal template='task/form.html' as modal_id %}{{ modal_id }}|{% render_static_modals %}
    """).render(RequestContext(RequestFactory().get('/'), {}))
    second_id = second_pass.split('|')[0].strip()

    assert first_id == second_id
    assert f'<template id="{second_id}" data-spire-modal>' in second_pass
