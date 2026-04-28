from __future__ import annotations

import heapq

from django_spire.contrib.sync.core.exceptions import (
    CircularDependencyError,
    UnknownDependencyError,
)


class DependencyGraph:
    def __init__(self, edges: dict[str, set[str]]) -> None:
        self._edges = {
            label: set(dependencies)
            for label, dependencies in edges.items()
        }

        all_labels = set(self._edges)

        for label, dependencies in self._edges.items():
            unknown = dependencies - all_labels

            if unknown:
                message = (
                    f'Model {label!r} declares dependencies on '
                    f'unknown models: {unknown}'
                )

                raise UnknownDependencyError(message)

        self._dependents: dict[str, set[str]] = {
            label: set() for label in self._edges
        }

        for label, dependencies in self._edges.items():
            for dep in dependencies:
                self._dependents[dep].add(label)

        self._order = self._compute_order()

    def _compute_order(self) -> list[str]:
        in_degree = {
            label: len(dependencies)
            for label, dependencies in self._edges.items()
        }

        heap = sorted(
            label
            for label, degree in in_degree.items()
            if degree == 0
        )

        heapq.heapify(heap)

        order: list[str] = []

        while heap:
            label = heapq.heappop(heap)
            order.append(label)

            for dependent in self._dependents[label]:
                in_degree[dependent] -= 1

                if in_degree[dependent] == 0:
                    heapq.heappush(heap, dependent)

        if len(order) != len(self._edges):
            missing = set(self._edges) - set(order)

            message = f'Circular dependency detected: {missing}'
            raise CircularDependencyError(message)

        return order

    def dependencies(self, label: str) -> set[str]:
        return set(self._edges.get(label, set()))

    def known_models(self) -> frozenset[str]:
        return frozenset(self._edges)

    def sync_order(self) -> list[str]:
        return list(self._order)
