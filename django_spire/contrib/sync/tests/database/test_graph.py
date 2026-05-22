from __future__ import annotations

import pytest

from django_spire.contrib.sync.core.exceptions import (
    CircularDependencyError,
    UnknownDependencyError,
)
from django_spire.contrib.sync.database.graph import DependencyGraph


def test_single_node_no_deps() -> None:
    graph = DependencyGraph({'a.A': set()})

    assert graph.sync_order() == ['a.A']


def test_linear_chain_ordered() -> None:
    graph = DependencyGraph({
        'a.A': set(),
        'b.B': {'a.A'},
        'c.C': {'b.B'},
    })

    order = graph.sync_order()

    assert order.index('a.A') < order.index('b.B')
    assert order.index('b.B') < order.index('c.C')


def test_diamond_ordered() -> None:
    graph = DependencyGraph({
        'a.A': set(),
        'b.B': {'a.A'},
        'c.C': {'a.A'},
        'd.D': {'b.B', 'c.C'},
    })

    order = graph.sync_order()

    assert order.index('a.A') < order.index('b.B')
    assert order.index('a.A') < order.index('c.C')
    assert order.index('b.B') < order.index('d.D')
    assert order.index('c.C') < order.index('d.D')


def test_unknown_dependency_raises() -> None:
    with pytest.raises(UnknownDependencyError):
        DependencyGraph({'a.A': {'missing.M'}})


def test_cycle_raises() -> None:
    with pytest.raises(CircularDependencyError):
        DependencyGraph({
            'a.A': {'b.B'},
            'b.B': {'a.A'},
        })


def test_sync_order_deterministic() -> None:
    edges = {
        'a.A': set(),
        'b.B': set(),
        'c.C': {'a.A', 'b.B'},
    }

    assert DependencyGraph(edges).sync_order() == DependencyGraph(edges).sync_order()


def test_known_models_matches_edges() -> None:
    edges = {'a.A': set(), 'b.B': {'a.A'}}
    graph = DependencyGraph(edges)

    assert graph.known_models() == frozenset({'a.A', 'b.B'})


def test_dependencies_returns_copy() -> None:
    edges = {'a.A': set(), 'b.B': {'a.A'}}
    graph = DependencyGraph(edges)

    deps = graph.dependencies('b.B')
    deps.add('mutation')

    assert graph.dependencies('b.B') == {'a.A'}
