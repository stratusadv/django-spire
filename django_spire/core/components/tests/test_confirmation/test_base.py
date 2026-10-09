from __future__ import annotations

from typing import Any

from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.components.confirmation import BaseConfirmationComponent
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

    def test_the_prompt_keeps_the_templates_wording_when_none_is_given(self) -> None:
        html = ' '.join(render_to_string(
            GreetingConfirmationComponent.template,
            {'component': GreetingConfirmationComponent()},
        ).split())

        assert 'Are you sure?' in html
        assert '</span> Confirm </button>' in html
        assert '<p>' not in html

    def test_the_prompt_is_worded_by_the_parameters_it_is_built_with(self) -> None:
        component = GreetingConfirmationComponent(
            title='Send the greeting?',
            message='Everyone <b>will</b> see it.',
            confirm_label='Send',
        )

        html = ' '.join(render_to_string(component.template, {'component': component}).split())

        assert 'Send the greeting?' in html
        assert 'Are you sure?' not in html
        assert '<p>Everyone &lt;b&gt;will&lt;/b&gt; see it.</p>' in html
        assert '</span> Send </button>' in html

    def test_confirm_requires_the_access_the_class_declares(self) -> None:
        assert self._required_confirm_access(GreetingConfirmationComponent()) == Glue.Access.VIEW
        assert self._required_confirm_access(GuardedConfirmationComponent()) == Glue.Access.CHANGE
