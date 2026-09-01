from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db import models

    from django_spire.core.search.command import SearchCommand
    from django_spire.core.search.search import Search


@dataclass
class SearchResult:
    search_key: str
    name: str
    icon: str | None = None
    label: str = ''
    description: str | None = None
    url: str = ''

    @classmethod
    def from_search(cls, search: Search, obj: models.Model) -> SearchResult:
        return cls(
            search_key=search.search_key,
            name=search.section_name,
            icon=search.icon,
            label=search.result_name(obj),
            description=search.result_description(obj),
            url=search.generate_detail_url(obj),
        )

    @classmethod
    def from_command(cls, search: Search, command: SearchCommand) -> SearchResult:
        return cls(
            search_key=search.search_key,
            name=search.section_name,
            icon=command.icon,
            label=command.name,
            description=command.description,
            url=command.url,
        )

    @classmethod
    def from_list(cls, search: Search, url: str) -> SearchResult:
        return cls(
            search_key=search.search_key,
            name=search.section_name,
            icon=search.icon,
            label=search.section_name,
            url=url,
        )
