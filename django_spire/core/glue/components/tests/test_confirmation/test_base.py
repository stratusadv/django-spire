from __future__ import annotations

from typing import Any

from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.glue.components.confirmation import BaseConfirmationComponent
from django_spire.core.tests.test_cases import BaseTestCase


class GreetingConfirmationComponent(BaseConfirmationComponent):
    def on_confirm(self) -> dict[str, Any]:
        return {'greeting': 'hello'}


class GuardedConfirmationComponent(GreetingConfirmationComponent):
    confirm_access = Glue.Access.CHANGE


class BaseConfirmationComponentTestCase(BaseTestCase):
    def _required_confirm_access(self, component: BaseConfirmationComponent) -> Glue.Access:
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session
        introduced = Glue.object(request, component)

        return introduced._resolve_required_access(
            introduced._bound_attributes['confirm'].definition.required_access
        )

    def test_confirming_fires_confirmed_with_what_the_action_returned(self) -> None:
        component = GreetingConfirmationComponent()

        component.confirm()

        assert component.__dict__['_pending_events'] == [
            {'name': 'confirmed', 'detail': {'greeting': 'hello'}},
        ]

    def test_cancelling_fires_cancelled_and_nothing_else(self) -> None:
        component = GreetingConfirmationComponent()

        component.cancel()

        assert component.__dict__['_pending_events'] == [{'name': 'cancelled', 'detail': {}}]

    def test_confirm_requires_the_access_the_class_declares(self) -> None:
        assert self._required_confirm_access(GreetingConfirmationComponent()) == Glue.Access.VIEW
        assert self._required_confirm_access(GuardedConfirmationComponent()) == Glue.Access.CHANGE
