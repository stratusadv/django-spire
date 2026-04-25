from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Archive(Protocol):
    def extract(self, archive_path: Path, target_dir: Path) -> list[Path]: ...
