from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.activity.context import activity_user
from django_spire.metric.domain.models import Domain, SubDomain


class DomainServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = Domain()

    def test_create_saves_and_adds_activity(self):
        with activity_user(self.super_user):
            domain, created = self.domain.services.save_model_obj(
                name='test_domain', description='test description'
            )

        assert created is True
        assert domain.pk is not None
        assert domain.name == 'test_domain'
        assert domain.activities.count() == 1
        assert domain.activities.first().verb == 'created'

    def test_update_saves_and_adds_activity(self):
        with activity_user(self.super_user):
            self.domain.services.save_model_obj(name='test_domain')

        with activity_user(self.super_user):
            domain, created = self.domain.services.save_model_obj(name='updated_domain')

        assert created is False
        assert domain.name == 'updated_domain'
        assert domain.activities.count() == 2
        assert domain.activities.order_by('created_datetime').last().verb == 'updated'


class SubDomainServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = Domain.objects.create(name='test_domain')
        self.subdomain = SubDomain(domain=self.domain)

    def test_create_saves_and_adds_activity(self):
        with activity_user(self.super_user):
            subdomain, created = self.subdomain.services.save_model_obj(name='test_subdomain')

        assert created is True
        assert subdomain.pk is not None
        assert subdomain.domain == self.domain
        assert subdomain.activities.count() == 1
        assert subdomain.activities.first().verb == 'created'
