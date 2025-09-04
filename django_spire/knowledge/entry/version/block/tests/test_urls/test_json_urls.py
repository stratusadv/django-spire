import json

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.tests.factories import create_test_version_block


class EntryVersionBlockJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_version_block = create_test_version_block()

    def test_update_text_view_url_path(self):
        response = self.client.post(
            reverse('django_spire:knowledge:entry:version:block:json:update_text'),
            data=json.dumps({
                'pk': self.test_version_block.pk,
                'value': '',
                'block_type': 'text'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
