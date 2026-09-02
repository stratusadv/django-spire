from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django_glue import Glue
from django_spire.contrib.shortcuts import get_object_or_null_obj

from test_project.app.showcase import forms
from test_project.app.showcase.models import WidgetShowcase
from test_project.app.showcase.navigation import ShowcaseNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

# The live model panel's own fields -- scalars only. The relation fields
# (category, assigned_user, watchers, checkbox_tags, search_tags) are read
# through their *_display computed properties instead (auto-discovered via
# @Glue.property, no entry needed here), so the panel never puts a nested
# User proxy on the wire.
MODEL_FIELDS = [
    'boolean_field',
    'char_field',
    'color_field',
    'email_field',
    'password_field',
    'postal_code_field',
    'search_field',
    'slug_field',
    'telephone_field',
    'url_field',
    'uuid_field',
    'select_choice',
    'radio_choice',
    'date_field',
    'datetime_field',
    'time_field',
    'currency_field',
    'decimal_field',
    'float_field',
    'hidden_field',
    'big_integer_field',
    'integer_field',
    'positive_integer_field',
    'small_integer_field',
    'text_field',
]


@login_required()
def form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    showcase = get_object_or_null_obj(WidgetShowcase, pk=pk)

    # Registering the form nested on the model (rather than a standalone
    # Glue.form()) is what lets the page hold a live-updating read view of
    # the same instance: Glue.model.widget_showcase_model.form edits it,
    # Glue.model.widget_showcase_model.load_state() re-reads it after save.
    Glue.model(
        request,
        'widget_showcase_model',
        showcase,
        Glue.Access.CHANGE,
        fields=MODEL_FIELDS,
        form=forms.WidgetShowcaseForm,
    )

    nav = ShowcaseNavigation()
    nav.page_title = 'Widget Showcase'

    return TemplateResponse(
        request=request, context=nav.as_context(), template='showcase/page/form_page.html'
    )
