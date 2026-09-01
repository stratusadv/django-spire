from dataclasses import dataclass
from enum import Enum


class SearchCommandAction(Enum):
    DISPATCH_MODAL = 'dispatch_modal'
    OPEN_URL_CURRENT_TAB = 'open_url_in_current_tab'
    OPEN_URL_NEW_TAB = 'open_url_in_new_tab'


class SearchCommand:
    Action: type[SearchCommandAction] = SearchCommandAction

    def __init__(
            self,
            name: str,
            icon: str,
            url: str,
            action: SearchCommandAction,
            description: str | None = None,
            permission: str | None = None,
    ):
        self.name = name
        self.icon = icon
        self.url = url
        self.action = action
        self.description = description
        self.permission = permission
