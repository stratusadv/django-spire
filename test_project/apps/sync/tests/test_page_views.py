from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase

from test_project.apps.sync.tests.factories import (
    create_test_client,
    create_test_site,
    create_test_stake,
    create_test_survey_plan,
)


class SyncDemoPageViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_dashboard_returns_200(self):
        response = self.client.get(reverse('sync:page:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_list_clients_returns_200(self):
        response = self.client.get(reverse('sync:page:list', kwargs={'model': 'client'}))
        self.assertEqual(response.status_code, 200)

    def test_list_sites_returns_200(self):
        response = self.client.get(reverse('sync:page:list', kwargs={'model': 'site'}))
        self.assertEqual(response.status_code, 200)

    def test_list_plans_returns_200(self):
        response = self.client.get(reverse('sync:page:list', kwargs={'model': 'surveyplan'}))
        self.assertEqual(response.status_code, 200)

    def test_list_stakes_returns_200(self):
        response = self.client.get(reverse('sync:page:list', kwargs={'model': 'stake'}))
        self.assertEqual(response.status_code, 200)
