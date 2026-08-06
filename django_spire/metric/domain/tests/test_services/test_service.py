from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import Domain, SubDomain


class DomainServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = Domain()

    def test_create_saves_and_adds_activity(self):
        domain = self.domain.services.save_model_obj(
            user=self.super_user, name='test_domain', description='test description'
        )

        assert domain.pk is not None
        assert domain.name == 'test_domain'
        assert domain.activities.count() == 1
        assert domain.activities.first().verb == 'created'

    def test_update_saves_and_adds_activity(self):
        self.domain.services.save_model_obj(user=self.super_user, name='test_domain')

        domain = self.domain.services.save_model_obj(user=self.super_user, name='updated_domain')

        assert domain.name == 'updated_domain'
        assert domain.activities.count() == 2
        assert domain.activities.order_by('created_datetime').last().verb == 'updated'


class SubDomainServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = Domain.objects.create(name='test_domain')
        self.subdomain = SubDomain(domain=self.domain)

    def test_create_saves_and_adds_activity(self):
        subdomain = self.subdomain.services.save_model_obj(
            user=self.super_user, name='test_subdomain'
        )

        assert subdomain.pk is not None
        assert subdomain.domain == self.domain
        assert subdomain.activities.count() == 1
        assert subdomain.activities.first().verb == 'created'
