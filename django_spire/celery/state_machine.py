from celery import states


class CeleryTaskStateMachine:
    """Explicit state transition table for CeleryTasks.

    Terminal states (READY_STATES) are sticky; PENDING/RECEIVED are never
    entered after leaving; custom (progress) states are free-form and allowed
    from any non-terminal state, but a custom state never reverts to a plain
    STARTED. Same-state writes on non-terminal states are idempotent no-ops.
    """

    BASE = {
        states.PENDING: {states.STARTED, states.FAILURE, states.REVOKED, states.REJECTED},
        states.RECEIVED: {states.STARTED, states.FAILURE, states.REVOKED, states.REJECTED},
        states.STARTED: {states.SUCCESS, states.FAILURE, states.RETRY, states.REVOKED},
        states.RETRY: {states.STARTED, states.FAILURE, states.REVOKED},
        states.SUCCESS: set(),
        states.FAILURE: set(),
        states.REVOKED: set(),
        states.REJECTED: set(),
    }

    @staticmethod
    def _anchor(state: str) -> str:
        # custom/progress states ('MAKING NOISES') anchor to STARTED
        if state in states.READY_STATES or state in (
            states.PENDING,
            states.RECEIVED,
            states.RETRY,
            states.REVOKED,
            states.REJECTED,
        ):
            return state

        return states.STARTED

    @classmethod
    def ok(cls, current: str, to: str) -> bool:
        if to in states.READY_STATES:
            return current not in states.READY_STATES

        if current == to:
            return current not in states.READY_STATES

        if to in (states.PENDING, states.RECEIVED):
            return False

        if to not in states.ALL_STATES:
            return current not in states.READY_STATES

        return to in cls.BASE[cls._anchor(current)]
