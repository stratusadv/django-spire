from __future__ import annotations

import time
from typing import (
    TypeVar,
    Generic,
    Iterator,
    Callable,
    Any, TYPE_CHECKING,
)

from django.db.models import Manager
from pydantic import BaseModel

if TYPE_CHECKING:
    from django_spire.contrib.rest.client.model import RestModelClient

TSchema = TypeVar('TSchema', bound=BaseModel)

class RestQuerySet(Generic[TSchema]):
    def __init__(
        self,
        client: RestModelClient,
        rest_model_class: type[TSchema],
        *,
        # Internal state for cloning
        _request_params: dict[str, Any] | None = None,
        _filters: list[Callable[[TSchema], bool]] | None = None,
        _excludes: list[Callable[[TSchema], bool]] | None = None,
        _ordering: list[tuple[str, bool]] | None = None,
        _limit: int | None = None,
        _offset: int = 0,
        _cached_results: list[TSchema] | None = None,
    ):
        self.client = client
        self._request_params = _request_params
        self._rest_model_class = rest_model_class

        self._filters = _filters or []
        self._excludes = _excludes or []
        self._ordering = _ordering or []
        self._limit = _limit
        self._offset = _offset
        self._cached_results = _cached_results

    def _clone(
        self,
        **overrides
    ) -> RestQuerySet[TSchema]:
        """Create a copy with optional overrides. Clears cache unless explicitly passed."""
        return RestQuerySet(
            client=self.client,
            rest_model_class=self._rest_model_class,
            _request_params=overrides.get('_request_params', self._request_params),
            _filters=overrides.get('_filters', list(self._filters)),
            _excludes=overrides.get('_excludes', list(self._excludes)),
            _ordering=overrides.get('_ordering', list(self._ordering)),
            _limit=overrides.get('_limit', self._limit),
            _offset=overrides.get('_offset', self._offset),
            _cached_results=overrides.get('_cached_results'),
        )

    def _evaluate(self) -> list[TSchema]:
        """Fetch (if needed) and apply all post-processing."""
        if self._cached_results is not None:
            return self._cached_results


        start = time.perf_counter()

        if self._request_params:
            results = self.client.fetch_many(**self._request_params)
        else:
            results = self.client.fetch_many()

        end = time.perf_counter()
        elapsed = end - start
        print(f"Query execution time: {elapsed:.6f} seconds")

        # Apply filters
        for fn in self._filters:
            results = [x for x in results if fn(x)]

        # Apply excludes
        for fn in self._excludes:
            results = [x for x in results if not fn(x)]

        # Apply ordering (reverse for stable multi-key sort)
        for field, reverse in reversed(self._ordering):
            results.sort(key=lambda x: self._get_attr(x, field), reverse=reverse)

        # Apply offset/limit
        if self._offset:
            results = results[self._offset:]
        if self._limit is not None:
            results = results[:self._limit]

        self._cached_results = results
        return results

    @staticmethod
    def _get_attr(obj: Any, path: str) -> Any:
        """Get nested attribute using 'a__b__c' syntax."""
        for part in path.split('__'):
            if obj is None:
                return None
            obj = getattr(obj, part, None)
        return obj

    @staticmethod
    def _make_predicate(key: str, value: Any) -> Callable[[Any], bool]:
        """Create a predicate for Django-style field lookups."""
        parts = key.split('__')

        def predicate(obj: Any) -> bool:
            current = obj
            for part in parts:
                if current is None:
                    return False
                if hasattr(current, part):
                    current = getattr(current, part)
                elif isinstance(current, dict):
                    current = current.get(part)
                else:
                    return False
            return current == value

        return predicate

    def __iter__(self) -> Iterator[TSchema]:
        return iter(self._evaluate())

    def __len__(self) -> int:
        return len(self._evaluate())

    def __bool__(self) -> bool:
        return bool(self._evaluate())

    def __repr__(self) -> str:
        return f"<RestSchemaQuerySet [{self._rest_model_class.__name__}]>"

    def __getitem__(self, key: int | slice) -> TSchema | RestQuerySet[TSchema]:
        if isinstance(key, int):
            if key < 0:
                return self._evaluate()[key]
            result = self.offset(key).limit(1).first()
            if result is None:
                raise IndexError("RestSchemaQuerySet index out of range")
            return result
        elif isinstance(key, slice):
            clone = self
            start = key.start or 0
            if start:
                clone = clone.offset(start)
            if key.stop is not None:
                clone = clone.limit(key.stop - start)
            return clone
        raise TypeError(f"Invalid index type: {type(key)}")

    def add_prefetch_params(
        self,
        **kwargs,
    ) -> RestQuerySet[TSchema]:
        return self._clone(_request_params=kwargs)

    def all(
        self,
    ) -> RestQuerySet[TSchema]:
        return self._clone()

    def filter(
        self,
        predicate: Callable[[TSchema], bool] | None = None,
        **kwargs,
    ) -> RestQuerySet[TSchema]:
        """
        Filter results by predicate and/or field lookups.

        Examples:
            .filter(lambda p: p.weight > 100)
            .filter(name="pikachu")
            .filter(type__name="electric")
        """
        new_filters = list(self._filters)
        if predicate:
            new_filters.append(predicate)
        for key, value in kwargs.items():
            new_filters.append(self._make_predicate(key, value))
        return self._clone(_filters=new_filters)

    def exclude(
        self,
        predicate: Callable[[TSchema], bool] | None = None,
        **kwargs,
    ) -> RestQuerySet[TSchema]:
        """Exclude results matching predicate or field lookups."""
        new_excludes = list(self._excludes)
        if predicate:
            new_excludes.append(predicate)
        for key, value in kwargs.items():
            new_excludes.append(self._make_predicate(key, value))
        return self._clone(_excludes=new_excludes)

    def order_by(self, *fields: str) -> RestQuerySet[TSchema]:
        """
        Order by fields. Prefix with '-' for descending.

        Examples:
            .order_by('name')
            .order_by('-weight', 'name')
        """
        ordering = []
        for field in fields:
            if field.startswith('-'):
                ordering.append((field[1:], True))
            else:
                ordering.append((field, False))
        return self._clone(_ordering=ordering)

    def limit(self, n: int) -> RestQuerySet[TSchema]:
        return self._clone(_limit=n)

    def offset(self, n: int) -> RestQuerySet[TSchema]:
        return self._clone(_offset=n)

    def first(self) -> TSchema | None:
        results = self._evaluate()
        return results[0] if results else None

    def last(self) -> TSchema | None:
        results = self._evaluate()
        return results[-1] if results else None

    def count(self) -> int:
        return len(self)

    def exists(self) -> bool:
        return bool(self)

    def get(
        self,
        request_params: dict[str, Any] | None = None,
        **kwargs,
    ) -> TSchema:
        """
        Return exactly one result matching kwargs.
        Raises LookupError if zero or multiple results.
        """
        if request_params:
            return self.client.fetch_one(**request_params)

        results = list(self.filter(**kwargs) if kwargs else self)
        if len(results) == 0:
            raise LookupError(f"No {self._rest_model_class.__name__} found")
        if len(results) > 1:
            raise LookupError(f"Multiple {self._rest_model_class.__name__} found")
        return results[0]

    def values_list(self, *fields: str, flat: bool = False) -> list[tuple] | list[Any]:
        """Extract field values from results."""
        if flat and len(fields) != 1:
            raise ValueError("flat=True requires exactly one field")

        results = self._evaluate()
        if flat:
            return [self._get_attr(item, fields[0]) for item in results]
        return [tuple(self._get_attr(item, f) for f in fields) for item in results]
