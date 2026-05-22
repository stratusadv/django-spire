from __future__ import annotations

import uuid

from typing import Any, TYPE_CHECKING

from django.db import connections

from django_spire.contrib.sync.django.storage import DjangoSyncStorage
from django_spire.contrib.sync.tests.factories import make_record as _factory_make_record
from django_spire.contrib.sync.tests.models import SyncTestModel, SyncTestSimpleModel

if TYPE_CHECKING:
    import threading

    from collections.abc import Callable

    from django_spire.contrib.sync.database.record import SyncRecord


def close_connections() -> None:
    connections.close_all()


def make_storage(batch_size_max: int = 5_000) -> DjangoSyncStorage:
    return DjangoSyncStorage(
        models=[SyncTestModel, SyncTestSimpleModel],
        identity_field='id',
        batch_size_max=batch_size_max,
    )


def make_named_record(key: str, name: str, ts: int, value: int = 0) -> SyncRecord:
    return _factory_make_record(
        key=key,
        data={'id': key, 'name': name, 'value': value},
        timestamps={'name': ts, 'value': ts},
    )


def uuid_from_ints(a: int, b: int) -> str:
    return str(uuid.UUID(int=(a << 64) | b))


def thread_safe(
    target: Callable[..., Any],
    errors: list[Exception],
    barrier: threading.Barrier | None = None,
    barrier_timeout: float = 5.0,
    catch: tuple[type[BaseException], ...] = (Exception,),
    on_caught: dict[type[BaseException], list[BaseException]] | None = None,
) -> Callable[..., None]:
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            if barrier is not None:
                barrier.wait(timeout=barrier_timeout)

            target(*args, **kwargs)
        except catch as exc:
            if on_caught is not None:
                for exc_type, bucket in on_caught.items():
                    if isinstance(exc, exc_type):
                        bucket.append(exc)
                        return

            errors.append(exc)
        finally:
            close_connections()

    return wrapper
