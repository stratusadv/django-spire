from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.user_account import factories


class UserAccountFactoriesUnitTestCase(BaseTestCase):
    def test_get_or_create_user_profile(self):
        profile = factories.get_or_create_user_profile(self.super_user)
        self.assertEqual(profile.user, self.super_user)
