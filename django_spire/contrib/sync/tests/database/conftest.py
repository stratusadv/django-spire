from __future__ import annotations

from typing import Any, TYPE_CHECKING
from unittest.mock import patch

import pytest

from django_spire.contrib.sync.tests.database.helpers import InMemoryDatabaseStorage, MODEL
from django_spire.contrib.sync.tests.factories import make_manifest

if TYPE_CHECKING:
    from django_spire.contrib.sync.database.manifest import SyncManifest


@pytest.fixture(autouse=True)
def _fixed_time() -> Any:
    with patch('django_spire.contrib.sync.database.engine.time') as mock_time:
        mock_time.time.return_value = 1000
        yield mock_time


@pytest.fixture
def storage() -> InMemoryDatabaseStorage:
    return InMemoryDatabaseStorage([MODEL])


@pytest.fixture
def empty_response() -> SyncManifest:
    return make_manifest(node_id='server', checkpoint=500, node_time=500)
