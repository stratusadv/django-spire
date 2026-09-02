from django_spire.api.choices import ApiPermissionChoices
from django_spire.api.forms import ApiAccessCreateForm
from django_spire.api.models import ApiAccess
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase


class ApiAccessCreateFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.regular_user = AuthUser.objects.create_user(username='regular')

    def test_superuser_can_grant_super_access(self) -> None:
        form = ApiAccessCreateForm(
            {'name': 'Key', 'permission': ApiPermissionChoices.VIEW, 'has_super_access': True},
            user=self.super_user,
        )
        assert 'has_super_access' in form.fields
        assert form.is_valid()

        api_access = form.save()
        assert api_access.has_super_access

    def test_non_superuser_cannot_grant_super_access(self) -> None:
        form = ApiAccessCreateForm(
            {'name': 'Key', 'permission': ApiPermissionChoices.VIEW, 'has_super_access': True},
            user=self.regular_user,
        )
        assert 'has_super_access' not in form.fields
        assert form.is_valid()

        api_access = form.save()
        assert not api_access.has_super_access

    def test_without_user_cannot_grant_super_access(self) -> None:
        form = ApiAccessCreateForm(
            {'name': 'Key', 'permission': ApiPermissionChoices.VIEW, 'has_super_access': True}
        )
        assert 'has_super_access' not in form.fields
        assert form.is_valid()

        api_access = form.save()
        assert not api_access.has_super_access

    def test_superuser_can_create_without_super_access(self) -> None:
        form = ApiAccessCreateForm(
            {'name': 'Key', 'permission': ApiPermissionChoices.VIEW}, user=self.super_user
        )
        assert form.is_valid()

        api_access = form.save()
        assert not api_access.has_super_access
        assert ApiAccess.objects.filter(pk=api_access.pk, name='Key').exists()
