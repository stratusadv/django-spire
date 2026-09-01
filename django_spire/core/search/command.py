from dataclasses import dataclass


@dataclass
class SearchCommand:
    search_key: str = ''
    name: str = ''
    icon: str = ''
    url: str = ''
    description: str | None = None
    permission: str | None = None
