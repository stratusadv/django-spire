from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase

from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()

    def test_str(self):
        assert str(self.domain) == str(self.domain.name)


class SubDomainModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)

    def test_str(self):
        assert str(self.subdomain) == str(self.subdomain.name)
