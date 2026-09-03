from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django_spire.core.search.command import SearchCommand

if TYPE_CHECKING:
    from django.db import models

    from django_spire.core.search.search import Search


@dataclass
class SearchResult:
    search_key: str
    name: str
    icon: str | None = None
    label: str = ''
    description: str | None = None
    url: str = ''
    action: SearchCommand.Action = SearchCommand.Action.OPEN_URL_CURRENT_TAB

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
            action=command.action,
        )

    @classmethod
    def from_list(cls, search: Search, url: str) -> SearchResult:
        return cls(
            search_key=search.search_key,
            name=search.section_name,
            icon=search.icon or 'bi-list-columns',
            label=search.section_name,
            description='list',
            url=url,
        )

    def generate_tag_attributes(self) -> str:
        if self.action == SearchCommand.Action.OPEN_URL_CURRENT_TAB:
            return f'href="{self.url}"'
        elif self.action == SearchCommand.Action.OPEN_URL_NEW_TAB:
            return f'href="{self.url}" target="_blank"'
        elif self.action == SearchCommand.Action.DISPATCH_MODAL:
            return f'href="#" @click="Spire.modal.dispatchView(\'{self.url}\')"'
        else:
            return f'href="{self.url}"'
