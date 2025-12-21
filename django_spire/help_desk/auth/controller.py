from __future__ import annotations

from django_spire.auth.controller.controller import BaseAuthController


class BaseHelpDeskAuthController(BaseAuthController):
    def can_add(self):
        return self.request.user.has_perm('django_spire_help_desk.add_helpdeskticket')

    def can_change(self):
        return self.request.user.has_perm('django_spire_help_desk.change_helpdeskticket')

    def can_delete(self):
        return self.request.user.has_perm('django_spire_help_desk.delete_helpdeskticket')

    def can_view(self):
        return self.request.user.has_perm('django_spire_help_desk.view_helpdeskticket')
