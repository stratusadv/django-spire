from django.test import TestCase, RequestFactory
from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.models import ApiAccess
from django_spire.api.choices import ApiAccessLevelChoices

class ApiKeySecurityTestCase(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.key = "test_secret_key"
        self.access = ApiAccess.objects.create(name="Security Test", level=ApiAccessLevelChoices.ADD)
        self.access.set_key_and_save(self.key)

    def test_authenticate_success(self):
        security = ApiKeySecurity()
        self.assertTrue(security.authenticate(None, self.key))

    def test_authenticate_fail_wrong_key(self):
        security = ApiKeySecurity()
        self.assertFalse(security.authenticate(None, "wrong_key"))

    def test_authenticate_fail_none_key(self):
        security = ApiKeySecurity()
        self.assertFalse(security.authenticate(None, None))

    def test_authenticate_level_required_success(self):
        # Access is ADD (2), level required is VIEW (1) -> True
        security = ApiKeySecurity(access_level_required=ApiAccessLevelChoices.VIEW)
        self.assertTrue(security.authenticate(None, self.key))
        
        # Access is ADD (2), level required is ADD (2) -> True
        security = ApiKeySecurity(access_level_required=ApiAccessLevelChoices.ADD)
        self.assertTrue(security.authenticate(None, self.key))

    def test_authenticate_level_required_fail(self):
        # Access is ADD (2), level required is CHANGE (3) -> False
        security = ApiKeySecurity(access_level_required=ApiAccessLevelChoices.CHANGE)
        self.assertFalse(security.authenticate(None, self.key))

    def test_get_key_from_header(self):
        security = ApiKeySecurity()
        request = self.rf.get('/', HTTP_API_KEY=self.key)
        self.assertEqual(security._get_key(request), self.key)
        
        request = self.rf.get('/', **{'HTTP_USER_KEY': self.key})
        self.assertEqual(security._get_key(request), self.key)

    def test_get_key_from_query(self):
        security = ApiKeySecurity()
        request = self.rf.get(f'/?api_key={self.key}')
        self.assertEqual(security._get_key(request), self.key)

    def test_get_key_precedence(self):
        # Header should be checked first in the loop but actually it checks param names in order
        # and for each param name it checks header then query.
        security = ApiKeySecurity()
        request = self.rf.get(f'/?api_key=query_key', HTTP_API_KEY='header_key')
        
        # 'api_key' is first in _API_KEY_PARAM_NAMES
        # headers.get('api_key') is checked first.
        # RequestFactory maps HTTP_API_KEY to header 'api_key'
        self.assertEqual(security._get_key(request), 'header_key')
