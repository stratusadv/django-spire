from __future__ import annotations

from django.test import Client, TestCase

from django_spire.user_account.tests.factories import create_super_user


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.super_user = create_super_user()
        self.client.force_login(self.super_user)

    def tearDown(self):
        pass
