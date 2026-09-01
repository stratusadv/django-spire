from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.template.response import TemplateResponse
from django.utils.dateparse import parse_datetime

from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib.utils import get_object_from_module_string
from django_spire.metric.domain.navigation import DomainNavigation
from django_spire.metric.report.models import ReportRun
from django_spire.metric.report.registry import ReportRegistry

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


_UNSET = object()


def _coerce_argument_value(annotation_class: type, value: str) -> object:
    try:
        return annotation_class(value)
    except (TypeError, ValueError):
        return _UNSET


def _bool_argument_value(request: WSGIRequest, argument: str) -> bool:
    return request.GET.get(argument, '').lower() == 'true'


def _date_argument_value(request: WSGIRequest, argument: str) -> object:
    date_str = request.GET.get(argument, None)

    if not date_str:
        return None

    parsed = parse_datetime(date_str)

    if not parsed:
        return _UNSET

    return parsed.date()


def _datetime_argument_value(request: WSGIRequest, argument: str) -> object:
    datetime_str = request.GET.get(argument, None)

    if not datetime_str:
        return None

    parsed = parse_datetime(datetime_str)

    if parsed is None:
        return _UNSET

    return parsed


def _multi_select_argument_value(request: WSGIRequest, argument: str) -> list[str]:
    return request.GET.getlist(argument, [])


def _report_argument_value(
    request: WSGIRequest, argument: str, run_argument: dict[str, Any]
) -> object:
    annotation = run_argument['annotation']

    if annotation == 'bool':
        return _bool_argument_value(request, argument)

    if annotation == 'date':
        return _date_argument_value(request, argument)

    if annotation == 'datetime':
        return _datetime_argument_value(request, argument)

    if annotation == 'multi_select':
        return _multi_select_argument_value(request, argument)

    value = request.GET.get(argument, None)

    if not value:
        return None

    return _coerce_argument_value(run_argument['annotation_class'], value)


@permission_required('django_spire_metric_report.view_reportrun')
def report_view(request: WSGIRequest) -> TemplateResponse:
    nav = DomainNavigation()
    nav.page_title = 'Reports'
    nav.page_description = 'More Reporting Info'

    nav.breadcrumbs.add('Reports', 'django_spire:metric:report:page:report')

    page_report_registry = ReportRegistry()

    for report_registry in settings.DJANGO_SPIRE_REPORT_REGISTRIES:
        report_registry_class = get_object_from_module_string(report_registry)

        page_report_registry.add_registry(report_registry_class())

    context: dict[str, Any] = {}

    context['registry'] = page_report_registry

    if request.GET:
        report_key_stack = request.GET.get('report_key_stack', None)

        if report_key_stack:
            report = page_report_registry.get_report_from_key_stack(report_key_stack)

            if report:
                for key in report_key_stack.split('|'):
                    nav.breadcrumbs.add(name=key)

                context['report_run_arguments'] = report.run_arguments

                context['report_run_arguments_values'] = {}

                for argument, run_argument in context['report_run_arguments'].items():
                    get_request_value = _report_argument_value(request, argument, run_argument)

                    if get_request_value is _UNSET:
                        context.setdefault('report_invalid_arguments', []).append(argument)
                        get_request_value = None

                    context['report_run_arguments_values'][argument] = get_request_value

                if request.GET.get('report_should_run', 'false').lower() == 'true':
                    missing_arguments = [
                        argument
                        for argument, value in context['report_run_arguments_values'].items()
                        if value is None and context['report_run_arguments'][argument]['required']
                    ]

                    if not missing_arguments:
                        ReportRun.objects.create(report_key_stack=report_key_stack)
                        report.run(**context['report_run_arguments_values'])
                    else:
                        context['report_missing_arguments'] = missing_arguments

                context['report'] = report
                context['report_run_count'] = ReportRun.objects.run_count(report_key_stack)

    else:
        top_ten_report_runs = [
            {
                **report_run,
                'report_key_stack_verbose': report_run['report_key_stack'].replace('|', ' > '),
            }
            for report_run in ReportRun.objects.by_top_ten()
        ]

        context['top_ten_report_runs'] = top_ten_report_runs

    context.update(nav.as_context())

    return TemplateResponse(
        request, 'django_spire/metric/report/page/report_page.html', context=context
    )
