from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase

from test_project.apps.sync.tests.factories import (
    create_test_client,
    create_test_site,
    create_test_stake,
    create_test_survey_plan,
)


class ClientModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client_obj = create_test_client()

    def test_str_returns_name(self):
        self.assertEqual(str(self.client_obj), self.client_obj.name)


class SiteModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.site = create_test_site()

    def test_str_returns_name(self):
        self.assertEqual(str(self.site), self.site.name)

    def test_status_default(self):
        self.assertEqual(self.site.status, 'active')


class SurveyPlanModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan = create_test_survey_plan()

    def test_str_contains_site_name(self):
        self.assertIn(self.plan.site.name, str(self.plan))


class StakeModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.stake = create_test_stake()

    def test_str_returns_label(self):
        self.assertEqual(str(self.stake), self.stake.label)
