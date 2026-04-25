from __future__ import annotations

from typing import Callable, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Source(Protocol):
    def download(
        self,
        remote_path: str,
        local_path: Path,
        callback: Callable[[int, int], None] | None = None,
    ) -> None: ...

    def list_dir(self, remote_path: str) -> list[str]: ...
