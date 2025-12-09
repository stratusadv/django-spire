from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection


class CollectionFormUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()

    def test_create_form_view_url_path(self):
        response = self.client.get(
            reverse('django_spire:knowledge:collection:form:create')
        )
        assert response.status_code == 200

    def test_create_with_parent_form_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:collection:form:create_with_parent',
                kwargs={'parent_pk': self.collection.pk}
            )
        )
        assert response.status_code == 200

    def test_update_form_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:collection:form:update',
                kwargs={'pk': self.collection.pk}
            )
        )
        assert response.status_code == 200
