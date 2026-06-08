from __future__ import annotations

from django.template.response import TemplateResponse

from django_spire.changelog.validators import get_validated_changelog


def changelog_rows_view(request) -> TemplateResponse:  # noqa: ANN001
    batch_size = int(request.GET.get('batch_size', 20))
    page = int(request.GET.get('page', 1))
    changelog_items = get_validated_changelog()
    total_count = len(changelog_items)
    start = (page - 1) * batch_size
    end = start + batch_size
    items = list(changelog_items[start:end])
    context = {
        'items': items,
        'has_next': total_count > end,
        'total_count': total_count,
        'batch_size': batch_size,
    }
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/contrib/changelog/content/changelog_content.html',
    )
