from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.test import RequestFactory, TestCase

from django_spire.contrib.session.controller import SessionController
from django_spire.contrib.session.templatetags.session_tags import session_controller_to_json


class TestSessionController(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(self.request)

        self.shopping_cart_session = SessionController(
            request=self.request,
            session_key='shopping_cart'
        )

    def test_add_data(self) -> None:
        key = 'currency'
        value = 'CAD'

        self.shopping_cart_session.add_data(key, value)

        assert key in self.shopping_cart_session.data
        assert self.shopping_cart_session.data[key] == value

    def test_data_property_returns_dict(self) -> None:
        assert isinstance(self.shopping_cart_session.data, dict)

    def test_getitem(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')

        assert self.shopping_cart_session['currency'] == 'CAD'

    def test_has_data_false_when_empty(self) -> None:
        assert self.shopping_cart_session.has_data is False

    def test_has_data_true_when_data_exists(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')

        assert self.shopping_cart_session.has_data is True

    def test_has_data_false_after_remove(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.remove_data('currency')

        assert self.shopping_cart_session.has_data is False

    def test_is_expired_false_when_not_expired(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')

        assert self.shopping_cart_session.is_expired is False

    def test_is_expired_true_when_expired(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.seconds_till_expiry = -5
        self.shopping_cart_session._set_timeout_datestamp()

        assert self.shopping_cart_session.is_expired is True

    def test_purge_removes_session_data(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.purge()

        assert 'shopping_cart' not in self.request.session

    def test_remove_data(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.add_data('discount', None)
        self.shopping_cart_session.remove_data('currency')

        assert 'currency' not in self.shopping_cart_session.data
        assert 'discount' in self.shopping_cart_session.data

    def test_session_data_added_to_database(self) -> None:
        self.shopping_cart_session.add_data('favorites', ['cool_shirt', 'fun_hat'])
        self.request.session.save()

        session_key = self.request.session.session_key
        session_in_db = Session.objects.get(session_key=session_key)
        session_data = session_in_db.get_decoded()

        assert self.shopping_cart_session.session_key in session_data
        assert 'favorites' in session_data[self.shopping_cart_session.session_key]
        assert session_data[self.shopping_cart_session.session_key]['favorites'] == ['cool_shirt', 'fun_hat']

    def test_set_modified(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')

        assert self.request.session.modified is True

    def test_set_timeout_datestamp(self) -> None:
        self.shopping_cart_session._set_timeout_datestamp()

        assert '_timeout_datestamp' in self.shopping_cart_session.data
        assert datetime.now().timestamp() < self.shopping_cart_session['_timeout_datestamp']

    def test_setitem(self) -> None:
        key = 'currency'
        value = 'CAD'

        self.shopping_cart_session[key] = value

        assert key in self.shopping_cart_session.data
        assert self.shopping_cart_session.data[key] == value

    def test_timeout_datestamp_returns_float(self) -> None:
        self.shopping_cart_session._set_timeout_datestamp()

        assert isinstance(self.shopping_cart_session.timeout_datestamp, float)

    def test_timeout_datestamp_returns_zero_when_not_set(self) -> None:
        controller = SessionController(
            request=self.request,
            session_key='new_session'
        )

        assert controller.timeout_datestamp == 0

    def test_to_json_returns_string(self) -> None:
        self.shopping_cart_session.add_data('currency', 'CAD')
        self.shopping_cart_session.add_data('discount', None)

        assert isinstance(self.shopping_cart_session.to_json(), str)


class TestSessionControllerToJson(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def _create_context_with_session(self) -> MagicMock:
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)

        context = MagicMock()
        context.get.return_value = request

        return context

    def test_returns_escaped_json(self) -> None:
        context = self._create_context_with_session()

        result = session_controller_to_json(context, 'test_key')

        assert isinstance(result, str)

    def test_calls_context_get_with_request(self) -> None:
        context = self._create_context_with_session()

        session_controller_to_json(context, 'test_key')

        context.get.assert_called_once_with('request')

    def test_returns_safe_string(self) -> None:
        context = self._create_context_with_session()

        result = session_controller_to_json(context, 'test_key')

        assert hasattr(result, '__html__')
