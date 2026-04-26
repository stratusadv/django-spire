from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from django_spire.contrib.generic_views import portal_views

from test_project.apps.sync import models
from test_project.apps.sync.config import (
    TABLET_COUNT_MAX,
    get_active_sync_databases,
    get_active_tablet_databases,
)
from test_project.apps.sync.constants import (
    DEFAULT_STRATEGY,
    DashboardAction,
    SeedScenario,
    SyncMode,
)
from test_project.apps.sync.context import (
    get_current_database,
    get_tablet_count,
    set_tablet_count,
    switch_database,
)
from test_project.apps.sync.registry import (
    MODEL_MAP,
    STRATEGY_CHOICES,
)
from test_project.apps.sync.seeding.seed import (
    SCENARIO_CHOICES,
    seed_sync_scenario,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


def dashboard_page_view(request: WSGIRequest) -> TemplateResponse:
    tablet_count = _resolve_tablet_count(request)
    current_database = _resolve_current_database(tablet_count)
    is_cloud_view = current_database == 'cloud'
    active_tablet_database = current_database if not is_cloud_view else 'tablet_1'

    result = None
    seed_result = None
    has_sync = False
    sync_mode = ''
    merged_cloud_view = None
    cloud_database_view = None
    rows = None
    counts = None

    selected_strategy = request.POST.get('strategy', DEFAULT_STRATEGY)
    selected_scenario = request.POST.get('scenario', SeedScenario.LAND_SURVEY)
    seed_value = request.POST.get('seed', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == DashboardAction.SEED:
            seed_result = _handle_seed(selected_scenario, seed_value)

        elif action == DashboardAction.SYNC_CURRENT and not is_cloud_view:
            rows, counts, result, has_sync, sync_mode = _handle_sync_current(
                active_tablet_database, selected_strategy, tablet_count,
            )

        elif action == DashboardAction.SYNC_ALL:
            rows, counts, result, has_sync, sync_mode, merged_cloud_view = _handle_sync_all(
                active_tablet_database, selected_strategy, tablet_count, is_cloud_view,
            )

    if is_cloud_view:
        cloud_database_view = models.Client.services.transformation.build_cloud_database_view()
    elif rows is None:
        transformation = models.Client.services.transformation
        rows = transformation.classify_databases(tablet_database=active_tablet_database)
        counts = transformation.count_kinds(rows)

    return TemplateResponse(request, 'sync/page/dashboard_page.html', {
        'active_tablet_database': active_tablet_database,
        'cloud_database_view': cloud_database_view,
        'counts': counts,
        'current_database': current_database,
        'has_sync': has_sync,
        'is_cloud_view': is_cloud_view,
        'merged_cloud_view': merged_cloud_view,
        'result': result,
        'rows': rows,
        'scenario_choices': SCENARIO_CHOICES,
        'seed_result': seed_result,
        'seed_value': seed_value,
        'selected_scenario': selected_scenario,
        'selected_strategy': selected_strategy,
        'strategy_choices': STRATEGY_CHOICES,
        'sync_mode': sync_mode,
        'tablet_count': tablet_count,
        'tablet_count_max': TABLET_COUNT_MAX,
        'tablet_databases': get_active_tablet_databases(tablet_count),
    })


def detail_page_view(request: WSGIRequest, model: str, pk: int) -> TemplateResponse:
    if model not in MODEL_MAP:
        raise PermissionDenied

    model_class = MODEL_MAP[model]
    instance = get_object_or_404(model_class, pk=pk)

    context = {model: instance}

    if model == 'client':
        context['sites'] = list(instance.sites.all())
    elif model == 'site':
        context['plans'] = list(instance.plans.all())
    elif model == 'surveyplan':
        context['stakes'] = list(instance.stakes.all())

    return portal_views.detail_view(
        request,
        obj=instance,
        context_data=context,
        template=f'sync/page/{model}_detail_page.html',
    )


def list_page_view(request: WSGIRequest, model: str) -> TemplateResponse:
    if model not in MODEL_MAP:
        raise PermissionDenied

    model_class = MODEL_MAP[model]
    objects = list(model_class.objects.all())

    return TemplateResponse(request, 'sync/page/list_page.html', {
        'objects': objects,
        'model_name': model,
    })


def switch_database_view(request: WSGIRequest, database_name: str) -> HttpResponseRedirect:
    _ = request
    tablet_count = get_tablet_count()

    if database_name not in get_active_sync_databases(tablet_count):
        return redirect('sync:page:dashboard')

    switch_database(database_name)
    return redirect('sync:page:dashboard')


def verification_page_view(request: WSGIRequest) -> TemplateResponse:
    verification = models.Client.services.transformation.build_verification()

    return TemplateResponse(request, 'sync/page/verification_page.html', {
        'verification': verification,
    })


def _handle_seed(scenario: str, seed_value: str) -> dict:
    parsed_seed = int(seed_value) if seed_value.isdigit() else None
    return seed_sync_scenario(scenario=scenario, seed=parsed_seed)


def _handle_sync_all(
    active_tablet_database: str,
    strategy: str,
    tablet_count: int,
    is_cloud_view: bool,
) -> tuple:
    transformation = models.Client.services.transformation
    rows = transformation.classify_databases(tablet_database=active_tablet_database)
    counts = transformation.count_kinds(rows)

    result = models.Client.services.processor.perform_sync(
        strategy=strategy, tablet_count=tablet_count,
    )

    transformation.apply_resolutions(rows, result, tablet_database=active_tablet_database)

    merged_cloud_view = None

    if is_cloud_view:
        merged_cloud_view = transformation.build_merged_cloud_view(result)

    return rows, counts, result, True, SyncMode.ALL, merged_cloud_view


def _handle_sync_current(
    active_tablet_database: str,
    strategy: str,
    tablet_count: int,
) -> tuple:
    transformation = models.Client.services.transformation
    rows = transformation.classify_databases(tablet_database=active_tablet_database)
    counts = transformation.count_kinds(rows)

    result = models.Client.services.processor.perform_sync(
        strategy=strategy,
        tablet_count=tablet_count,
        tablet_databases=[active_tablet_database],
    )

    transformation.apply_resolutions(rows, result, tablet_database=active_tablet_database)

    return rows, counts, result, True, SyncMode.CURRENT


def _resolve_current_database(tablet_count: int) -> str:
    current_database = get_current_database()

    if current_database not in get_active_sync_databases(tablet_count):
        switch_database('tablet_1')
        return 'tablet_1'

    return current_database


def _resolve_tablet_count(request: WSGIRequest) -> int:
    tablet_count_raw = request.POST.get('tablet_count', '')

    if tablet_count_raw.isdigit():
        set_tablet_count(int(tablet_count_raw))

    return get_tablet_count()
