from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.utils import get_object_from_module_string
from django_spire.metric.domain.navigation import DomainNavigation
from django_spire.metric.report.models import ReportRun
from django_spire.metric.report.registry import ReportRegistry
from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('report').permission_required('can_view')
def report_view(request: WSGIRequest) -> TemplateResponse:
    nav = DomainNavigation()
    nav.page_title = 'Reports'
    nav.page_description = 'More Reporting Info'

    nav.breadcrumbs.add('Reports', 'django_spire:metric:report:page:report')

    page_report_registry = ReportRegistry()

    for report_registry in settings.DJANGO_SPIRE_REPORT_REGISTRIES:
        report_registry_class = get_object_from_module_string(report_registry)

        page_report_registry.add_registry(report_registry_class())

    context = {}

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

                for argument in context['report_run_arguments']:
                    if context['report_run_arguments'][argument]['annotation'] == 'bool':
                        get_request_value = request.GET.get(argument, False)

                    elif context['report_run_arguments'][argument]['annotation'] == 'date':
                        date_str = request.GET.get(argument, None)

                        if date_str:
                            get_request_value = datetime.strptime(date_str, '%Y-%m-%d').date()
                        else:
                            get_request_value = date_str

                    elif context['report_run_arguments'][argument]['annotation'] == 'datetime':
                        datetime_str = request.GET.get(argument, None)

                        if datetime_str:
                            get_request_value = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
                        else:
                            get_request_value = datetime_str

                    elif (
                        context['report_run_arguments'][argument]['annotation']
                        == 'multi_select'
                    ):
                        get_request_value = request.GET.getlist(argument, [])

                    else:
                        value = request.GET.get(argument, None)

                        if value:
                            get_request_value = context['report_run_arguments'][argument][
                                'annotation_class'
                            ](value)
                        else:
                            get_request_value = value

                    context['report_run_arguments_values'][argument] = get_request_value

                if request.GET.get('report_should_run', 'false').lower() == 'true':
                    for argument, value in context['report_run_arguments_values'].items():
                        if value is None:
                            break
                    else:
                        ReportRun.objects.create(report_key_stack=report_key_stack)
                        report.run(**context['report_run_arguments_values'])

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
