from datetime import datetime

from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session

from django_spire.contrib.session.tests.factories import ShoppingCartSession


class BaseSessionTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        # Attach real session
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(self.request)

        self.shopping_cart_session = ShoppingCartSession(self.request)

    def test_base_session_add_data(self):
        key = 'currency'
        value = 'CAD'

        self.shopping_cart_session.add_data(key, value)
        self.assertIn(key, self.shopping_cart_session.data)
        self.assertEqual(self.shopping_cart_session.data[key], value)

    def test_base_session_set_item(self):
        key = 'currency'
        value = 'CAD'

        self.shopping_cart_session[key] = value
        self.assertIn(key, self.shopping_cart_session.data)
        self.assertEqual(self.shopping_cart_session.data[key], value)

    def test_base_session_remove_data(self):
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.add_data('discount', None)
        self.shopping_cart_session.remove_data('currency')

        self.assertNotIn('currency', self.shopping_cart_session.data)
        self.assertIn('discount', self.shopping_cart_session.data)

    def test_set_session_modified(self):
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.assertTrue(self.request.session.modified)

    def test_session_has_data(self):
        self.assertFalse(self.shopping_cart_session.has_data)

        self.shopping_cart_session.add_data('currency', 'CAD')
        self.assertTrue(self.shopping_cart_session.has_data)


        self.shopping_cart_session.remove_data('currency')
        self.assertFalse(self.shopping_cart_session.has_data)

    def test_session_data_to_json(self):
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.add_data('discount', None)

        self.assertTrue(isinstance(self.shopping_cart_session.to_json(), str))

    def test_to_json_errors_when_not_json_serializable(self):
        self.shopping_cart_session.json_serializable = False

        with self.assertRaises(ValueError):
            self.shopping_cart_session.to_json()

    def test_set_timeout_datestamp(self):
        self.shopping_cart_session._set_timeout_datestamp()
        self.assertIn('_timeout_datestamp', self.shopping_cart_session.data)
        self.assertTrue(datetime.now().timestamp() < self.shopping_cart_session['_timeout_datestamp'])

    def test_session_data_expiry(self):
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.assertFalse(self.shopping_cart_session.is_expired)

        self.shopping_cart_session.seconds_till_expiry = -5
        self.shopping_cart_session._set_timeout_datestamp()
        self.assertTrue(self.shopping_cart_session.is_expired)

    def test_session_data_added_to_database(self):
        # Add something to the session
        self.shopping_cart_session.add_data('favorites', ['cool_shirt', 'fun_hat'] )
        self.request.session.save()

        # Get session from DB using session_key
        session_key = self.request.session.session_key
        session_in_db = Session.objects.get(session_key=session_key)

        # Decode the session data
        session_data = session_in_db.get_decoded()

        self.assertIn(self.shopping_cart_session.session_key, session_data)
        self.assertIn('favorites', session_data[self.shopping_cart_session.session_key])
        self.assertEqual(
            session_data[self.shopping_cart_session.session_key]['favorites'],
            ['cool_shirt', 'fun_hat']
        )

