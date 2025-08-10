from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.tests.factories import \
    create_test_entry_version


class EntryPageUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.collection = create_test_collection()
        self.test_entry = create_test_entry(
            collection=self.collection
        )
        self.test_entry_version = create_test_entry_version(
            entry=self.test_entry
        )
        self.test_entry.current_version = self.test_entry_version
        self.test_entry.save()

    def test_form_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:form:create',
                kwargs={'collection_pk': self.collection.pk}
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:form:update',
                kwargs={
                    'pk': self.test_entry.pk,
                    'collection_pk': self.collection.pk
                }
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_import_form_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:form:import',
                kwargs={'collection_pk': self.collection.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
