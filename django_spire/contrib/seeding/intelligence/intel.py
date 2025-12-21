from __future__ import annotations

from typing import Iterator

from dandy import BaseIntel


class SeedingIntel(BaseIntel):
    items: list[dict]

    def __iter__(self) -> Iterator[dict]:
        return iter(self.items)


class SourceIntel(BaseIntel):
    file_name: str
    python_source_code: str
