from __future__ import annotations

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.test import RequestFactory

from django_spire.auth.user.admin import AuthUserAdmin
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase


class AuthUserAdminTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.site = AdminSite()
        self.admin = AuthUserAdmin(AuthUser, self.site)
        self.request = RequestFactory().get('/')
        self.request.user = self.super_user

    def test_extends_django_user_admin(self) -> None:
        assert isinstance(self.admin, UserAdmin)

    def test_change_form_does_not_expose_a_writable_password_field(self) -> None:
        form = self.admin.get_form(self.request, obj=self.super_user, change=True)

        password_field = form.base_fields.get('password')

        assert password_field is None or isinstance(password_field, ReadOnlyPasswordHashField)

    def test_saving_the_change_form_does_not_store_a_raw_password(self) -> None:
        original_hash = self.super_user.password

        form_class = self.admin.get_form(self.request, obj=self.super_user, change=True)
        form = form_class(instance=self.super_user, data={})

        assert 'password' not in form.fields or not form.fields['password'].has_changed(
            original_hash,
            'plaintext',
        )

    def test_add_form_hashes_the_password(self) -> None:
        form_class = self.admin.get_form(self.request, obj=None, change=False)

        data = {
            'username': 'hashed_user',
            'password1': 'a-long-test-passphrase-42',
            'password2': 'a-long-test-passphrase-42',
        }

        form = form_class(data=data)

        assert form.is_valid(), form.errors

        user = form.save()

        assert user.password != 'a-long-test-passphrase-42'
        assert user.check_password('a-long-test-passphrase-42')
