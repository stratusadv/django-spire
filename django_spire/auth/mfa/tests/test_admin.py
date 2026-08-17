from __future__ import annotations

from django.contrib.admin.sites import AdminSite

from django_spire.auth.mfa.admin import MfaCodeAdmin
from django_spire.auth.mfa.models import MfaCode
from django_spire.core.tests.test_cases import BaseTestCase


class MfaCodeAdminTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.site = AdminSite()
        self.admin = MfaCodeAdmin(MfaCode, self.site)
        self.mfa_code = MfaCode.generate_code(self.super_user)

    def test_code_is_not_in_list_display(self) -> None:
        assert 'code' not in self.admin.list_display

    def test_code_is_not_searchable(self) -> None:
        assert 'code' not in self.admin.search_fields

    def test_code_is_not_rendered_in_any_list_column(self) -> None:
        rendered = []

        for column in self.admin.list_display:
            attribute = getattr(self.admin, column, None)

            if callable(attribute):
                rendered.append(str(attribute(self.mfa_code)))
            else:
                rendered.append(str(getattr(self.mfa_code, column, '')))

        assert str(self.mfa_code.code) not in ' '.join(rendered)

    def test_codes_cannot_be_created_or_edited(self) -> None:
        assert not self.admin.has_add_permission(None)
        assert not self.admin.has_change_permission(None)

    def test_user_link_renders(self) -> None:
        result = self.admin.user_link(self.mfa_code)

        assert self.super_user.username in result
