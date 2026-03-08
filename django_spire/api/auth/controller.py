from __future__ import annotations

from django_spire.auth.controller.controller import BaseAuthController


class BaseApiAuthController(BaseAuthController):
    def can_add(self):
        return self.request.user.has_perm('django_spire_api.add_apiaccess')

    def can_change(self):
        return self.request.user.has_perm('django_spire_api.change_apiaccess')

    def can_delete(self):
        return self.request.user.has_perm('django_spire_api.delete_apiaccess')

    def can_view(self):
        return self.request.user.has_perm('django_spire_api.view_apiaccess')
