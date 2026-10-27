from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.redirects import safe_redirect_url
from django_spire.metric.domain.statistic.models import StatisticValue

from test_project.app.metrics.metrics import StoreMetric
from test_project.app.metrics.navigation import MetricsNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect

RECORD_ACTIONS = {
    'created_web': {
        'domain': 'store',
        'sub_domain': 'web',
        'statistic_group': 'orders',
        'statistic': 'created',
        'value': 3,
        'reference': ['order', 'created'],
        'label': 'Record 3 orders created (web)',
    },
    'created_retail': {
        'domain': 'store',
        'sub_domain': 'retail',
        'statistic_group': 'orders',
        'statistic': 'created',
        'value': 1,
        'reference': ['order', 'created', 'checkout'],
        'label': 'Record 1 order created (retail, via checkout)',
    },
    'revenue_web': {
        'domain': 'store',
        'sub_domain': 'web',
        'statistic_group': 'orders',
        'statistic': 'revenue',
        'value': 42.5,
        'reference': ['order', 'invoiced'],
        'label': 'Record 42.50 order revenue (web)',
    },
}


@login_required()
def record_test_page_view(request: WSGIRequest) -> TemplateResponse:
    values = (
        StatisticValue.objects.filter(
            statistic__key__in=StoreMetric.stored_keys()['statistics'],
            sub_domain__key__in=StoreMetric.stored_keys()['subdomains'],
        )
        .select_related('statistic', 'sub_domain')
        .order_by('-timestamp')[:25]
    )

    nav = MetricsNavigation()
    nav.page_title = 'Metric Record Test'

    context = nav.as_context()
    context['actions'] = RECORD_ACTIONS
    context['values'] = values

    return TemplateResponse(request, context=context, template='metrics/page/record_test_page.html')


@login_required()
def record_click_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action in RECORD_ACTIONS:
            spec = RECORD_ACTIONS[action]
            worker = StoreMetric.record(
                spec['domain'],
                spec['sub_domain'],
                spec['statistic_group'],
                spec['statistic'],
                spec['reference'],
                spec['value'],
            )
            worker.join()

    return redirect(safe_redirect_url(request, fallback=reverse('metrics:page:record_test')))
