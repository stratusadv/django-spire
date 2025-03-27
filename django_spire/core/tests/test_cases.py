from __future__ import annotations

import tempfile

from django.test import Client, override_settings, TestCase

from django_spire.user_account.tests.factories import create_super_user


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()

        self.super_user = create_super_user()
        self.client.force_login(self.super_user)
