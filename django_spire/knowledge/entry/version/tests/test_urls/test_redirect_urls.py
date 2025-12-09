from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.choices import EntryVersionStatusChoices
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryVersionRedirectUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.test_entry = create_test_entry(collection=self.collection)
        self.test_entry_version = create_test_entry_version(entry=self.test_entry)
        self.test_entry.current_version = self.test_entry_version
        self.test_entry.save()

    def test_publish_view_redirects(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:redirect:publish',
                kwargs={'pk': self.test_entry_version.pk}
            )
        )
        assert response.status_code == 302

    def test_publish_view_updates_status(self):
        self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:redirect:publish',
                kwargs={'pk': self.test_entry_version.pk}
            )
        )
        self.test_entry_version.refresh_from_db()
        assert self.test_entry_version.status == EntryVersionStatusChoices.PUBLISHED
