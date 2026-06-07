from django.test import TestCase


class QuerySetFilterTestCase(TestCase):

    def setUp(self):
        super().setUp()

    def test_error_on_missing_filter_key(self):
        pass
