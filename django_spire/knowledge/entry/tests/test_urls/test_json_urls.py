from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.tests.factories import create_test_entry


class EntryJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_entry = create_test_entry()

    def test_reorder_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:json:reorder',
                kwargs={'pk': self.test_entry.pk, 'order': 0}
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_update_files_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:json:update_files',
            )
        )

        self.assertEqual(response.status_code, 200)