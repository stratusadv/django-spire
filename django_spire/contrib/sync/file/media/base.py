from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Store(Protocol):
    def download(self, key: str, target_path: Path) -> None: ...
    def list_keys(self, prefix: str) -> set[str]: ...
    def upload(self, key: str, source_path: Path, content_type: str | None = None) -> str: ...
