from django_spire.core.tests.test_cases import BaseTestCase
from django.test import RequestFactory
from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.models import ApiAccess
from django_spire.api.choices import ApiPermissionChoices


class ApiKeySecurityTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.rf = RequestFactory()
        self.key = 'test_secret_key'
        self.access = ApiAccess.objects.create(
            name='Security Test', permission=ApiPermissionChoices.ADD
        )
        self.access.set_key_and_save(self.key)

    def test_authenticate_success_returns_api_access(self) -> None:
        security = ApiKeySecurity()
        result = security.authenticate(None, self.key)
        assert result == self.access
        assert result.name == 'Security Test'
        assert result.permission == ApiPermissionChoices.ADD

    def test_authenticate_returns_user_for_limiting_access(self) -> None:
        security = ApiKeySecurity()
        self.access.user = self.super_user
        self.access.save()
        result = security.authenticate(None, self.key)
        assert result.user == self.super_user

    def test_authenticate_fail_wrong_key(self) -> None:
        security = ApiKeySecurity()
        assert not security.authenticate(None, 'wrong_key')

    def test_authenticate_fail_none_key(self) -> None:
        security = ApiKeySecurity()
        assert not security.authenticate(None, None)

    def test_authenticate_level_required_success(self) -> None:
        # Access is ADD (2), level required is VIEW (1) -> True, returns instance
        security = ApiKeySecurity(permission_required=ApiPermissionChoices.VIEW)
        assert security.authenticate(None, self.key) == self.access

        # Access is ADD (2), level required is ADD (2) -> True, returns instance
        security = ApiKeySecurity(permission_required=ApiPermissionChoices.ADD)
        assert security.authenticate(None, self.key) == self.access

    def test_authenticate_level_required_fail(self) -> None:
        # Access is ADD (2), level required is CHANGE (3) -> False
        security = ApiKeySecurity(permission_required=ApiPermissionChoices.CHANGE)
        assert not security.authenticate(None, self.key)

    def test_get_key_from_header(self) -> None:
        security = ApiKeySecurity()
        request = self.rf.get('/', HTTP_API_KEY=self.key)
        assert security._get_key(request) == self.key

        request = self.rf.get('/', HTTP_USER_KEY=self.key)
        assert security._get_key(request) == self.key

    def test_get_key_from_query(self) -> None:
        security = ApiKeySecurity()
        request = self.rf.get(f'/?api_key={self.key}')
        assert security._get_key(request) == self.key

    def test_get_key_precedence(self) -> None:
        # Header should be checked first in the loop but actually it checks param names in order
        # and for each param name it checks header then query.
        security = ApiKeySecurity()
        request = self.rf.get('/?api_key=query_key', HTTP_API_KEY='header_key')

        # 'api_key' is first in _API_KEY_PARAM_NAMES
        # headers.get('api_key') is checked first.
        # RequestFactory maps HTTP_API_KEY to header 'api_key'
        assert security._get_key(request) == 'header_key'
