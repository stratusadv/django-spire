from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class CollectionFormUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_form_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:collection:form:create',
            )
        )

        self.assertEqual(response.status_code, 200)
