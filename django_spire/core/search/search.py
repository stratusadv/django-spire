from __future__ import annotations

from abc import ABC, abstractmethod

from django.db import models
from django.http.request import HttpRequest

from django_spire.core.search.command import SearchCommand
from django_spire.core.search.result import SearchResult


class Search(ABC):
    Command: type[SearchCommand] = SearchCommand

    model_class: type[models.Model] | None = None
    searchable_fields: list[str] | None = None
    searchable_commands: list[SearchCommand] = []
    name: str
    icon: str
    permission_required: str | None = None
    result_limit: int = 10

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        required_attributes = 'name', 'icon'

        for attribute in required_attributes:
            if getattr(cls, attribute, None) is None:
                message = f'{cls.__name__}.{attribute} is None and must be defined'
                raise ValueError(message)

    @property
    def section_name(self) -> str:
        return self.name

    @abstractmethod
    def base_queryset(self, request: HttpRequest) -> models.QuerySet:
        raise NotImplementedError

    @abstractmethod
    def generate_list_url(self) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def generate_detail_url(self, obj: models.Model) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def result_description(self, obj: models.Model) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def result_name(self, obj: models.Model) -> str:
        raise NotImplementedError

    def search(self, request: HttpRequest, query_string: str | None) -> models.QuerySet | None:
        if self.searchable_fields is None:
            return None

        query_string = (query_string or '').strip()

        if not query_string:
            return None

        if not self.searchable_fields:
            return self.model_class.objects.none()

        words = query_string.split(' ')

        queryset = self.base_queryset(request)

        for word in words:
            conditions = models.Q()

            for field in self.searchable_fields:
                conditions |= models.Q(**{f'{field}__icontains': word})

            queryset = queryset.filter(conditions)

        return queryset[: self.result_limit]

    def to_result(self, obj: models.Model) -> SearchResult:
        return SearchResult.from_search(self, obj)

    def commands_for_query(self, query_string: str) -> list[SearchCommand]:
        query = (query_string or '').strip().lower()

        if not query:
            return []

        words = query.split(' ')

        return [
            command
            for command in self.searchable_commands
            if all(word in command.name.lower() for word in words)
        ]

    def list_result(self, query_string: str) -> SearchResult | None:
        query = (query_string or '').strip().lower()

        if not query:
            return None

        if self.model_class is not None:
            keywords = (
                self.name,
                self.model_class._meta.verbose_name,
                self.model_class._meta.verbose_name_plural,
            )
        else:
            keywords = (self.name,)

        if not any(keyword and query in keyword.lower() for keyword in keywords):
            return None

        list_url = self.generate_list_url()

        if list_url is None:
            return None

        return SearchResult.from_list(self, list_url)

    def command_result(self, command: SearchCommand) -> SearchResult:
        return SearchResult.from_command(self, command)
