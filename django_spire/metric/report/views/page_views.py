from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.urls import reverse

from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views
from django_spire.core.utils import get_object_from_module_string
from django_spire.metric.report.models import ReportRun
from django_spire.metric.report.registry import ReportRegistry

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('report.view_report')
def report_view(request: WSGIRequest) -> TemplateResponse:
    breadcrumbs = Breadcrumbs()

    breadcrumbs.add_breadcrumb(
        'Reports',
        reverse('django_spire:metric:report:page:report'),
    )

    page_report_registry = ReportRegistry()

    for report_registry in settings.DJANGO_SPIRE_REPORT_REGISTRIES:
        report_registry_class = get_object_from_module_string(
            report_registry
        )

        page_report_registry.add_registry(
            report_registry_class()
        )

    context_data = {
        'registry': page_report_registry,
    }

    if request.GET:
        report_key_stack = request.GET.get('report_key_stack', None)

        if report_key_stack:
            report = page_report_registry.get_report_from_key_stack(report_key_stack)

            if report:
                for key in report_key_stack.split('|'):
                    breadcrumbs.add_breadcrumb(
                        key,
                    )

                context_data['report_run_arguments'] = report.run_arguments

                context_data['report_run_arguments_values'] = {}
                for argument in report.run_arguments:
                    if context_data['report_run_arguments'][argument]['annotation'] == 'bool':
                        get_request_value = request.GET.get(argument, False)
                    else:
                        get_request_value = request.GET.get(argument, None)

                    context_data['report_run_arguments_values'][argument] = get_request_value

                if request.GET.get('report_should_run', 'false').lower() == 'true':
                    for argument, value in context_data['report_run_arguments_values'].items():
                        if value is None:
                            break
                    else:
                        ReportRun.objects.create(
                            report_key_stack=report_key_stack,
                        )
                        report.run()

                context_data['report'] = report
                context_data['report_run_count'] = ReportRun.objects.run_count(report_key_stack)

    else:
        context_data['top_ten_report_runs'] = ReportRun.objects.by_top_ten()

    return portal_views.template_view(
        request,
        page_title = 'Reports',
        page_description = 'More Reporting Info',
        breadcrumbs = breadcrumbs,
        context_data=context_data,
        template='django_spire/metric/report/page/report_page.html'
    )
