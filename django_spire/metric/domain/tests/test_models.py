from __future__ import annotations

from django.db import IntegrityError

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import SubDomain
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

    def test_key_assigned_on_create(self):
        assert self.subdomain.key is not None

    def test_key_is_unique(self):
        duplicate = SubDomain(domain=self.domain, name='duplicate', key=self.subdomain.key)
        with pytest.raises(IntegrityError):
            duplicate.save()
