from __future__ import annotations

from django_spire.auth.controller.controller import BaseAuthController


class BaseReportAuthController(BaseAuthController):
    def can_add(self):
        return self.request.user.has_perm('django_spire_metric_report.add_reportrun')

    def can_change(self):
        return self.request.user.has_perm('django_spire_metric_report.change_reportrun')

    def can_delete(self):
        return self.request.user.has_perm('django_spire_metric_report.delete_reportrun')

    def can_view(self):
        return self.request.user.has_perm('django_spire_metric_report.view_reportrun')
