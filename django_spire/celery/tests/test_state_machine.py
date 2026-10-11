from __future__ import annotations

from celery import states
from django.test import SimpleTestCase

from django_spire.celery.state_machine import CeleryTaskStateMachine


class CeleryTaskStateMachineTestCase(SimpleTestCase):
    def test_queued_transitions_to_started(self) -> None:
        assert CeleryTaskStateMachine.ok(states.PENDING, states.STARTED)
        assert CeleryTaskStateMachine.ok(states.RECEIVED, states.STARTED)

    def test_retry_transitions_to_started(self) -> None:
        assert CeleryTaskStateMachine.ok(states.RETRY, states.STARTED)

    def test_started_transitions_to_terminals_and_retry(self) -> None:
        for to_state in (states.SUCCESS, states.FAILURE, states.RETRY, states.REVOKED):
            assert CeleryTaskStateMachine.ok(states.STARTED, to_state)

    def test_ready_terminals_are_sticky(self) -> None:
        every_state = (
            states.PENDING,
            states.RECEIVED,
            states.STARTED,
            states.RETRY,
            states.REVOKED,
            states.REJECTED,
            states.IGNORED,
            states.FAILURE,
            states.SUCCESS,
            'MAKING NOISES',
        )
        for current in (states.SUCCESS, states.FAILURE, states.REVOKED):
            for to_state in every_state:
                assert not CeleryTaskStateMachine.ok(current, to_state), (current, to_state)

    def test_never_returns_to_pending_or_received(self) -> None:
        for current in (states.STARTED, states.RETRY, states.REVOKED, 'MAKING NOISES'):
            assert not CeleryTaskStateMachine.ok(current, states.PENDING)
            assert not CeleryTaskStateMachine.ok(current, states.RECEIVED)

    def test_same_state_is_idempotent_for_non_ready_states(self) -> None:
        for state in (
            states.PENDING,
            states.RECEIVED,
            states.STARTED,
            states.RETRY,
            'MAKING NOISES',
        ):
            assert CeleryTaskStateMachine.ok(state, state)

    def test_custom_states_allowed_from_every_non_ready_state(self) -> None:
        for current in (
            states.PENDING,
            states.RECEIVED,
            states.STARTED,
            states.RETRY,
            states.REJECTED,
            'ANOTHER STATE',
        ):
            assert CeleryTaskStateMachine.ok(current, 'MAKING NOISES'), current

    def test_custom_state_does_not_revert_to_started(self) -> None:
        assert not CeleryTaskStateMachine.ok('MAKING NOISES', states.STARTED)

    def test_custom_state_transitions_to_terminals(self) -> None:
        assert CeleryTaskStateMachine.ok('MAKING NOISES', states.SUCCESS)
        assert CeleryTaskStateMachine.ok('MAKING NOISES', states.FAILURE)
        assert CeleryTaskStateMachine.ok('MAKING NOISES', states.REVOKED)

    def test_rejected_rows_do_not_resume(self) -> None:
        for to_state in (states.STARTED, states.RETRY, states.PENDING):
            assert not CeleryTaskStateMachine.ok(states.REJECTED, to_state)

    def test_ignored_anchors_like_a_custom_state(self) -> None:
        assert CeleryTaskStateMachine.ok(states.IGNORED, states.RETRY)
        assert CeleryTaskStateMachine.ok(states.IGNORED, states.SUCCESS)
        assert not CeleryTaskStateMachine.ok(states.IGNORED, states.STARTED)
        assert not CeleryTaskStateMachine.ok(states.IGNORED, states.PENDING)
