from __future__ import annotations

from typing import Any

import pytest

from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.components.confirmation import BaseConfirmationComponent, ConfirmationRefusedError
from django_spire.core.tests.test_cases import BaseTestCase


class GreetingConfirmationComponent(BaseConfirmationComponent):
    def on_confirm(self) -> dict[str, Any]:
        return {'greeting': 'hello'}


class GuardedConfirmationComponent(GreetingConfirmationComponent):
    confirm_access = Glue.Access.CHANGE


class RefusingConfirmationComponent(BaseConfirmationComponent):
    def on_confirm(self) -> dict[str, Any]:
        message = 'The greeting was already sent.'
        raise ConfirmationRefusedError(message)


class FailingConfirmationComponent(BaseConfirmationComponent):
    def on_confirm(self) -> dict[str, Any]:
        message = 'The mail server is down.'
        raise RuntimeError(message)


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

        response = component.confirm()

        assert response is None
        assert component.__dict__['_pending_events'] == [
            {'name': 'confirmed', 'detail': {'greeting': 'hello'}},
        ]

    def test_a_refused_action_reports_why_and_fires_nothing(self) -> None:
        component = RefusingConfirmationComponent()

        response = component.confirm()

        assert [message.to_dict()['message'] for message in response.messages] == [
            'The greeting was already sent.',
        ]
        assert response.messages[0].level_tag == 'error'
        assert component.__dict__.get('_pending_events', []) == []

    def test_an_action_that_fails_otherwise_still_raises(self) -> None:
        component = FailingConfirmationComponent()

        with pytest.raises(RuntimeError):
            component.confirm()

        assert component.__dict__.get('_pending_events', []) == []

    def test_cancelling_is_raised_in_the_browser_and_has_no_callable(self) -> None:
        html = render_to_string(
            GreetingConfirmationComponent.template,
            {'component': GreetingConfirmationComponent()},
        )

        assert "component.$dispatch('cancelled')" in html
        assert not hasattr(GreetingConfirmationComponent, 'cancel')

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
