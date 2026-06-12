from django.test import TestCase

from django_spire.contrib.navigation import Navigation


class TestNavigation(TestCase):
    def test_navigation_init(self):
        _ = Navigation()
        assert True