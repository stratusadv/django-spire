from django_spire.auth.controller.controller import BaseAuthController

_METRIC_VIEW_PERMISSIONS = (
    'django_spire_metric_domain.view_domain',
    'django_spire_metric_domain.view_subdomain',
    'django_spire_metric_domain.view_statisticgroup',
    'django_spire_metric_domain.view_statistic',
    'django_spire_metric_domain.view_statisticvalue',
    'django_spire_metric_visual.view_visual',
    'django_spire_metric_visual.view_visualcondition',
    'django_spire_metric_visual.view_indicatorvisual',
    'django_spire_metric_visual.view_linechartvisual',
    'django_spire_metric_visual.view_barchartvisual',
    'django_spire_metric_visual.view_areachartvisual',
    'django_spire_metric_visual.view_piechartvisual',
    'django_spire_metric_visual.view_gaugechartvisual',
    'django_spire_metric_visual_presentation.view_presentation',
    'django_spire_metric_visual_presentation.view_slide',
    'django_spire_metric_visual_presentation.view_slidesection',
    'django_spire_metric_visual_signage.view_signage',
    'django_spire_metric_visual_signage.view_signagepresentation',
    'django_spire_metric_report.view_reportrun',
)


class BaseMetricAuthController(BaseAuthController):
    def _has_permission(self, action: str) -> bool:
        return any(
            self.request.user.has_perm(permission.replace('view_', f'{action}_'))
            for permission in _METRIC_VIEW_PERMISSIONS
        )

    def can_add(self) -> bool:
        return self._has_permission('add')

    def can_change(self) -> bool:
        return self._has_permission('change')

    def can_delete(self) -> bool:
        return self._has_permission('delete')

    def can_view(self) -> bool:
        return self._has_permission('view')
