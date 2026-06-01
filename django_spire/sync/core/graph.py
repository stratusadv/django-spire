from __future__ import annotations

import heapq

from django_spire.sync.core.exceptions import (
    CircularDependencyError,
    InvalidParameterError,
    UnknownDependencyError,
)


class DependencyGraph:
    def __init__(
        self,
        edges: dict[str, set[str]],
        deferred_edges: dict[str, set[str]] | None = None,
    ) -> None:
        for label in edges:
            if not label:
                message = 'edges must not contain empty labels'
                raise InvalidParameterError(message)

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

        self._deferred_edges: dict[str, set[str]] = {}

        if deferred_edges:
            for label, targets in deferred_edges.items():
                if not targets:
                    continue

                if label not in all_labels:
                    message = (
                        f'Deferred edge source {label!r} '
                        f'is not a known model'
                    )

                    raise InvalidParameterError(message)

                unknown = targets - all_labels

                if unknown:
                    message = (
                        f'Deferred edges from {label!r} reference '
                        f'unknown models: {unknown}'
                    )

                    raise UnknownDependencyError(message)

                self._deferred_edges[label] = set(targets)

        self._dependents: dict[str, set[str]] = {
            label: set() for label in self._edges
        }

        for label, dependencies in self._edges.items():
            for dependency in dependencies:
                self._dependents[dependency].add(label)

        self._order = self._compute_order()

    def _compute_order(self) -> list[str]:
        nodes_max = len(self._edges)

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

        for _ in range(nodes_max):
            if not heap:
                break

            label = heapq.heappop(heap)
            order.append(label)

            for dependent in self._dependents[label]:
                in_degree[dependent] -= 1

                if in_degree[dependent] < 0:
                    message = (
                        f'Negative in-degree for '
                        f'{dependent!r}: graph corrupted'
                    )

                    raise CircularDependencyError(message)

                if in_degree[dependent] == 0:
                    heapq.heappush(heap, dependent)

        if len(order) != nodes_max:
            missing = set(self._edges) - set(order)

            message = f'Circular dependency detected: {missing}'
            raise CircularDependencyError(message)

        return order

    @property
    def deferred_edges(self) -> dict[str, frozenset[str]]:
        return {
            label: frozenset(targets)
            for label, targets in self._deferred_edges.items()
        }

    def dependencies(self, label: str) -> set[str]:
        return set(self._edges.get(label, set()))

    def has_deferred_edges(self) -> bool:
        return bool(self._deferred_edges)

    def known_models(self) -> frozenset[str]:
        return frozenset(self._edges)

    def sync_order(self) -> list[str]:
        return list(self._order)
