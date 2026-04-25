from __future__ import annotations

from typing import TYPE_CHECKING

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
from test_project.apps.sync.context import (
    get_current_db,
    get_tablet_count,
    set_tablet_count,
    switch_db,
)
from test_project.apps.sync.seeding.seed import (
    SCENARIO_CHOICES,
    seed_sync_scenario,
)
from test_project.apps.sync.services.processor_service import (
    DEFAULT_STRATEGY,
    STRATEGY_CHOICES,
    SyncProcessorService,
)
from test_project.apps.sync.services.transformation_service import SyncTransformationService

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


def dashboard_page_view(request: WSGIRequest) -> TemplateResponse:
    result = None
    seed_result = None
    selected_strategy = request.POST.get('strategy', DEFAULT_STRATEGY)
    selected_scenario = request.POST.get('scenario', 'land_survey')
    seed_value = request.POST.get('seed', '').strip()
    has_sync = False
    sync_mode = ''
    merged_cloud_view = None
    cloud_database_view = None
    rows = None
    counts = None

    tablet_count_raw = request.POST.get('tablet_count', '')

    if tablet_count_raw.isdigit():
        set_tablet_count(int(tablet_count_raw))

    tablet_count = get_tablet_count()
    current_db = get_current_db()

    if current_db not in get_active_sync_databases(tablet_count):
        switch_db('tablet_1')
        current_db = 'tablet_1'

    is_cloud_view = current_db == 'cloud'
    active_tablet_db = current_db if not is_cloud_view else 'tablet_1'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'seed':
            parsed_seed = int(seed_value) if seed_value.isdigit() else None
            seed_result = seed_sync_scenario(
                scenario=selected_scenario,
                seed=parsed_seed,
            )

        if action == 'sync_current' and not is_cloud_view:
            transformation = SyncTransformationService()
            rows = transformation.classify_databases(tablet_db=active_tablet_db)
            counts = transformation.count_kinds(rows)

            processor = SyncProcessorService()
            result = processor.perform_sync(
                strategy=selected_strategy,
                tablet_count=tablet_count,
                tablet_dbs=[active_tablet_db],
            )

            has_sync = True
            sync_mode = 'current'
            transformation.apply_resolutions(rows, result, tablet_db=active_tablet_db)

        if action == 'sync_all':
            transformation = SyncTransformationService()
            rows = transformation.classify_databases(tablet_db=active_tablet_db)
            counts = transformation.count_kinds(rows)

            processor = SyncProcessorService()
            result = processor.perform_sync(
                strategy=selected_strategy,
                tablet_count=tablet_count,
            )

            has_sync = True
            sync_mode = 'all'
            transformation.apply_resolutions(rows, result, tablet_db=active_tablet_db)

            if is_cloud_view:
                merged_cloud_view = transformation.build_merged_cloud_view(result)

    if is_cloud_view:
        transformation = SyncTransformationService()
        cloud_database_view = transformation.build_cloud_database_view()
    elif rows is None:
        transformation = SyncTransformationService()
        rows = transformation.classify_databases(tablet_db=active_tablet_db)
        counts = transformation.count_kinds(rows)

    return TemplateResponse(request, 'sync/page/dashboard_page.html', {
        'active_tablet_db': active_tablet_db,
        'cloud_database_view': cloud_database_view,
        'counts': counts,
        'current_db': current_db,
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
    model_map = {
        'client': models.Client,
        'site': models.Site,
        'surveyplan': models.SurveyPlan,
        'stake': models.Stake,
    }

    if model not in model_map:
        raise PermissionDenied

    model_cls = model_map[model]
    obj = get_object_or_404(model_cls, pk=pk)

    context = {model: obj}

    if model == 'site':
        context['plans'] = list(obj.plans.all())
    elif model == 'surveyplan':
        context['stakes'] = list(obj.stakes.all())
    elif model == 'client':
        context['sites'] = list(obj.sites.all())

    return portal_views.detail_view(
        request,
        obj=obj,
        context_data=context,
        template=f'sync/page/{model}_detail_page.html'
    )


def list_page_view(request: WSGIRequest, model: str) -> TemplateResponse:
    model_map = {
        'client': models.Client,
        'site': models.Site,
        'surveyplan': models.SurveyPlan,
        'stake': models.Stake,
    }

    if model not in model_map:
        raise PermissionDenied

    model_cls = model_map[model]
    objects = list(model_cls.objects.all())

    return TemplateResponse(request, 'sync/page/list_page.html', {
        'objects': objects,
        'model_name': model,
    })


def switch_db_view(request: WSGIRequest, db_name: str) -> HttpResponseRedirect:
    _ = request
    tablet_count = get_tablet_count()

    if db_name not in get_active_sync_databases(tablet_count):
        return redirect('sync:page:dashboard')

    switch_db(db_name)
    return redirect('sync:page:dashboard')


def verification_page_view(request: WSGIRequest) -> TemplateResponse:
    transformation = SyncTransformationService()
    verification = transformation.build_verification()

    return TemplateResponse(request, 'sync/page/verification_page.html', {
        'verification': verification,
    })
