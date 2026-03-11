from __future__ import annotations

from typing_extensions import TYPE_CHECKING
from django_spire.contrib.generic_views.portal_views import infinite_scrolling_view
from django_spire.contrib.changelog.validators import get_validated_changelog

if TYPE_CHECKING:
    from django.template.response import TemplateResponse


def changelog_rows_view(request) -> TemplateResponse:
    return infinite_scrolling_view(
        request,
        context_data={'batch_size': 20},
        queryset=get_validated_changelog(),
        queryset_name='changelog',
        template='django_spire/contrib/changelog/content/changelog_content.html',
    )
