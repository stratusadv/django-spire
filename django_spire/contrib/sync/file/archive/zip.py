from __future__ import annotations

import logging
import zipfile

from enum import Enum
from pathlib import Path

from django_spire.contrib.sync.file.archive.base import Archive


logger = logging.getLogger(__name__)


class CollisionStrategy(Enum):
    RAISE = 'raise'
    SKIP = 'skip'
    OVERWRITE = 'overwrite'


class ZipArchive(Archive):
    def __init__(
        self,
        encoding: str = 'utf-8',
        flatten: bool = True,
        collision: CollisionStrategy = CollisionStrategy.RAISE,
    ) -> None:
        self._encoding = encoding
        self._flatten = flatten
        self._collision = collision

    def _resolve_target(
        self,
        info: zipfile.ZipInfo,
        target_dir: Path,
    ) -> Path:
        if self._flatten:
            return target_dir / Path(info.filename).name

        target = (target_dir / info.filename).resolve()

        if not target.is_relative_to(target_dir.resolve()):
            message = f'Path traversal detected in archive entry: {info.filename!r}'
            raise ValueError(message)

        return target

    def extract(self, archive_path: Path, target_dir: Path) -> list[Path]:
        target_dir.mkdir(parents=True, exist_ok=True)

        seen: set[str] = set()
        extracted: list[Path] = []

        with zipfile.ZipFile(archive_path, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue

                target = self._resolve_target(info, target_dir)

                if not target.name:
                    continue

                target_key = str(target)

                if target_key in seen:
                    if self._collision is CollisionStrategy.RAISE:
                        message = (
                            f'Duplicate target {target} in archive '
                            f'{archive_path} (from {info.filename!r})'
                        )
                        raise FileExistsError(message)

                    if self._collision is CollisionStrategy.SKIP:
                        logger.debug(
                            'Skipping duplicate %s from %s',
                            target,
                            info.filename,
                        )
                        continue

                seen.add(target_key)

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(info.filename))
                extracted.append(target)

        logger.info(
            'Extracted %d files from %s to %s',
            len(extracted),
            archive_path,
            target_dir,
        )

        return extracted
