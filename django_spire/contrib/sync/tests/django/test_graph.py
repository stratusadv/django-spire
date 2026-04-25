from __future__ import annotations

import pytest

from django_spire.contrib.sync.django.graph import build_graph
from django_spire.contrib.sync.tests.models import (
    SyncTestModel,
    SyncTestSimpleModel,
)


@pytest.mark.django_db
def test_simple_model_has_no_dependencies() -> None:
    graph = build_graph([SyncTestSimpleModel])

    assert graph.dependencies(SyncTestSimpleModel._meta.label) == set()


@pytest.mark.django_db
def test_build_graph_returns_topological_order() -> None:
    graph = build_graph([SyncTestModel, SyncTestSimpleModel])

    order = graph.sync_order()

    assert SyncTestModel._meta.label in order
    assert SyncTestSimpleModel._meta.label in order
