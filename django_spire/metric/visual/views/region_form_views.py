from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_glue import Glue

from django_spire.conf import settings
from django_spire.metric.visual import forms, models
from django_spire.metric.visual.navigation import VisualNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect

    from django_spire.metric.visual.models import Visual


def _region_status_rows(visual: Visual) -> list[dict]:
    registry = settings.DJANGO_SPIRE_METRIC_VISUAL_REGIONS

    regions_by_key = {
        region.key: region for region in models.VisualRegion.objects.filter(key__in=registry)
    }

    rows = []
    for key in registry:
        region = regions_by_key.get(key)

        if region is None or region.visual_id is None:
            status = 'unassigned'
        elif region.visual_id == visual.pk:
            status = 'connected'
        else:
            status = 'taken'

        rows.append({'key': key, 'status': status, 'region': region})

    return rows


@permission_required('django_spire_metric_visual.add_visualregion')
def connect_region_view(
    request: WSGIRequest, visual_pk: int
) -> TemplateResponse | HttpResponseRedirect:
    visual = get_object_or_404(models.Visual, pk=visual_pk)

    nav = VisualNavigation()
    nav.page_title = 'Connect to Region'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual), 'django_spire:metric:visual:page:detail', {'pk': visual.pk})
    nav.breadcrumbs.add('Connect to Region')
    context = nav.as_context()
    context['visual'] = visual
    context['region_rows'] = _region_status_rows(visual)

    return TemplateResponse(
        request, 'django_spire/metric/visual/page/connect_region_page.html', context
    )


@require_POST
@permission_required('django_spire_metric_visual.add_visualregion')
def connect_view(request: WSGIRequest, visual_pk: int) -> HttpResponseRedirect:
    visual = get_object_or_404(models.Visual, pk=visual_pk)
    key = request.POST.get('key', '')

    if key not in settings.DJANGO_SPIRE_METRIC_VISUAL_REGIONS:
        return redirect(reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk}))

    models.VisualRegion.objects.assign(key, visual)

    return redirect(reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk}))


@permission_required('django_spire_metric_visual.change_visualregion')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    region = get_object_or_404(models.VisualRegion, pk=pk)
    visual = region.visual

    form = forms.VisualRegionModelForm(request.POST or None, instance=region)

    Glue.form(request, 'visual_region_form', form, Glue.Access.DELETE)

    nav = VisualNavigation()
    nav.page_title = 'Edit Region'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual), 'django_spire:metric:visual:page:detail', {'pk': visual.pk})
    nav.breadcrumbs.add(str(region))
    nav.breadcrumbs.add('Edit')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Edit {region}'
    context['form_description'] = f'Region "{region.key}" for visual "{visual}".'
    context['visual'] = visual
    context['region'] = region

    return TemplateResponse(
        request, 'django_spire/metric/visual/page/region_form_page.html', context
    )


@require_POST
@permission_required('django_spire_metric_visual.change_visualregion')
def disconnect_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect:
    region = get_object_or_404(models.VisualRegion.objects.select_related('visual'), pk=pk)
    visual_pk = region.visual_id

    region.services.factory.disconnect()

    return redirect(
        request.GET.get(
            'return_url',
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual_pk}),
        )
    )
