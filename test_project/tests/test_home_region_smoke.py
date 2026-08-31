from django_spire.core.tests.test_cases import BaseTestCase


class HomeRegionSmokeTestCase(BaseTestCase):
    def test_home_page_renders_region_tags_without_error(self) -> None:
        response = self.client.get('/')

        assert response.status_code == 200
