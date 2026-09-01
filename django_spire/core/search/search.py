from __future__ import annotations

from abc import ABC, abstractmethod

from django.db import models

from django_spire.core.search.result import SearchResult


class BaseSearch(ABC):
    model_class: type[models.Model]
    searchable_fields: list[str]
    search_key: str
    name: str | None = None
    icon: str | None = None
    permission: str | None = None
    result_limit: int = 10

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        required_attributes = 'model_class', 'searchable_fields', 'search_key'

        for attribute in required_attributes:
            if getattr(cls, attribute, None) is None:
                message = f'{cls.__name__}.{attribute} is None and must be defined'
                raise ValueError(message)

    @property
    def section_name(self) -> str:
        if self.name:
            return self.name

        if self.model_class is not None:
            return self.model_class._meta.verbose_name_plural

        return self.search_key

    @abstractmethod
    def generate_url(self, obj: models.Model) -> str:
        raise NotImplementedError

    def result_description(self, obj: models.Model) -> str | None:  # noqa: ARG002
        return None

    def result_name(self, obj: models.Model) -> str:
        return str(obj)

    def base_queryset(self) -> models.QuerySet:
        manager = self.model_class.objects

        if hasattr(manager, 'not_deleted'):
            return manager.not_deleted()

        return manager.all()

    def search(self, query_string: str | None) -> models.QuerySet | None:
        query_string = (query_string or '').strip()

        if not query_string:
            return None

        if not self.searchable_fields:
            return self.model_class.objects.none()

        words = query_string.split(' ')

        queryset = self.base_queryset()

        for word in words:
            conditions = models.Q()

            for field in self.searchable_fields:
                conditions |= models.Q(**{f'{field}__icontains': word})

            queryset = queryset.filter(conditions)

        return queryset[: self.result_limit]

    def to_result(self, obj: models.Model) -> SearchResult:
        return SearchResult.from_search(self, obj)
