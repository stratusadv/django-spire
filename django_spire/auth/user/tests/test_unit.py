from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.auth.user.tests.factories import create_user


class UserProfileTestCase(BaseTestCase):
    def setUp(self):
        self.user = create_user(username='Wesley', password='goat_99')
