from __future__ import annotations

import re

from django import template
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe, SafeString


register = template.Library()

_UNSAFE_ID_CHARS_RE = re.compile(r'[^a-zA-Z0-9_-]+')
_STATIC_MODALS_REQUEST_ATTR = '_django_spire_static_modals'


def modal_id(template_path: str) -> str:
    """Deterministic `<template>` id for a modal content template path.

    Same template path -> same id, always -- so a caller never needs to
    invent/pass one, and a modal declared on one render (e.g. a full page
    load) stays correctly referenced by a trigger rendered on a later,
    separate render of the same template (e.g. a Glue.view fragment
    refresh), with no request-scoped bookkeeping required to keep the two
    in sync.
    """
    return 'modal-' + _UNSAFE_ID_CHARS_RE.sub('-', template_path)


register.filter('modal_id', modal_id)


def _render_modal_element(context: RequestContext, id: str, template: str) -> SafeString:
    content = render_to_string(
        template,
        context=context.flatten(),
        request=getattr(context, 'request', None),
    )
    return format_html(
        '<template id="{}" data-spire-modal>{}</template>',
        id,
        mark_safe(content),
    )


@register.simple_tag(takes_context=True)
def define_modal(
    context: RequestContext,
    id: str,
    template: str,
) -> SafeString:
    return _render_modal_element(context, id, template)


@register.simple_tag(takes_context=True)
def static_modal(context: RequestContext, template: str) -> str:
    """Queue a modal's `<template data-spire-modal>`, id derived from `template`.

    {% static_modal template='partner/agreement/company_rep/modal/content/company_rep_form_modal_content.html' as modal_id %}
    <a @click="await Spire.modal.open('{{ modal_id }}', { ... })">Add</a>

    Called "static" because the modal content template must render
    identically no matter which caller triggers it -- i.e. it can carry NO
    server-rendered, per-caller Django context of its own. All row-specific
    data has to arrive as scopeData passed to Spire.modal.open() at click
    time (JS), not baked into the template at render time. A modal that
    legitimately needs different server-rendered content per caller is not
    "static" and isn't a fit for this tag -- use {% define_modal %}
    instead, once per caller, with your own id.

    The id is derived deterministically from `template` (see the `modal_id`
    filter above) rather than invented per call, so:
    - Capturing it with `as` (as above) is the normal way to use it right
      next to a trigger, same as before -- but since it's the same id every
      time, you can also compute it independently anywhere else on the
      page with the `modal_id` filter (`{{ 'path/to/template.html'|modal_id }}`),
      with no shared request state needed to keep the two in sync. That
      includes a *separate* render of this same partial later (e.g. a
      Glue.view fragment refresh of a list card) -- the trigger rendered
      there resolves to the exact same id the original full-page render
      used.
    - Calling this more than once for the same template in one render
      (e.g. once per row in a list, for one shared edit-form modal, or
      once via `{% for %}` and again via a client-side `x-for` re-render of
      the same trigger markup) is deduped: only the first call actually
      renders and queues the `<template>` element; later calls for the
      same template are a noop. That keeps the DOM from filling up with N
      identical, unused copies when N rows each declare the same shared
      modal.

    Unlike {% define_modal %}, the `<template>` element itself isn't
    rendered inline at the call site -- it's queued on the request and
    drained once by {% render_static_modals %} (see
    django_spire/base/base.html, next to dispatch_modal.html). That keeps
    it out of the middle of a `{% for %}` loop's row markup, at one fixed
    location regardless of how many rows/renders declare it. A fragment
    view whose response never passes through base.html (e.g. one rendered
    for a Glue.view refresh) needs its own {% render_static_modals %} call
    so that response is self-contained.
    """
    id_ = modal_id(template)

    request = getattr(context, 'request', None)
    if request is None:
        _render_modal_element(context, id_, template)
        return id_

    queued_by_id = getattr(request, _STATIC_MODALS_REQUEST_ATTR, None)
    if queued_by_id is None:
        queued_by_id = {}
        setattr(request, _STATIC_MODALS_REQUEST_ATTR, queued_by_id)

    if id_ not in queued_by_id:
        queued_by_id[id_] = _render_modal_element(context, id_, template)

    return id_


@register.simple_tag(takes_context=True)
def render_static_modals(context: RequestContext) -> SafeString:
    """Drain and render every `<template>` element queued by {% static_modal %}
    earlier in this request's render. Place once, near dispatch_modal.html.
    """
    request = getattr(context, 'request', None)
    if request is None:
        return mark_safe('')

    queued_by_id = getattr(request, _STATIC_MODALS_REQUEST_ATTR, None)
    if not queued_by_id:
        return mark_safe('')

    setattr(request, _STATIC_MODALS_REQUEST_ATTR, {})
    return mark_safe(''.join(queued_by_id.values()))
