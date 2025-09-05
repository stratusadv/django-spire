from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.entry.version.models import EntryVersion


@AppAuthController('knowledge').permission_required('can_view')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    current_version = get_object_or_404(EntryVersion, pk=pk)
    entry = current_version.entry
    version_blocks = current_version.blocks.active().order_by('order')

    def breadcrumbs_func(breadcrumbs):
        breadcrumbs.add_breadcrumb(name='Knowledge')
        breadcrumbs.add_breadcrumb(
            name='Collections',
            href=reverse('django_spire:knowledge:collection:page:list')
        )
        breadcrumbs.add_breadcrumb(
            name=entry.collection.name,
            href=reverse(
                'django_spire:knowledge:collection:page:detail',
                kwargs={'pk': entry.collection.pk}
            )
        )
        breadcrumbs.add_breadcrumb(name=f'View {entry.name}')

    return portal_views.detail_view(
        request,
        obj=entry,
        breadcrumbs_func=breadcrumbs_func,
        context_data={
            'entry': entry,
            'current_version': current_version,
            'version_blocks': version_blocks,
        },
        template='django_spire/knowledge/entry/version/page/detail_page.html',
    )
