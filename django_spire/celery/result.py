import pickle
import logging

from celery.utils.serialization import get_pickled_exception

logger = logging.getLogger(__name__)


class SendFailedError(Exception):
    pass


class StaleStartedError(Exception):
    pass


class CeleryNoResult:
    def __str__(self) -> str:
        return 'No Result'


def set_pickled_no_result() -> bytes:
    return pickle.dumps(CeleryNoResult())


class CeleryExceptionResult:
    """Stored in CeleryTask._result for FAILURE CeleryTasks (sibling of CeleryNoResult).

    Built with Celery's own exception serialization (get_pickleable_exception):
    a picklable stand-in for the exception, falling back to
    UnpickleableExceptionWrapper when the exception itself is not picklable.
    """

    def __init__(
        self, exc: BaseException, einfo_pickle: bytes | None, traceback_text: str | None
    ) -> None:
        self.exc_type = type(exc).__name__
        self.message = str(exc)
        self.traceback = traceback_text
        self._einfo_pickle = einfo_pickle

    @property
    def exception(self) -> BaseException | None:
        # full restore only when picklable; same trust domain as the _result pickle
        if self._einfo_pickle is None:
            return None

        try:
            return get_pickled_exception(pickle.loads(self._einfo_pickle))
        except Exception:
            logger.exception('Failed to restore pickled exception for %s', self.exc_type)
            return None

    def __str__(self) -> str:
        return f'{self.exc_type}: {self.message}'
