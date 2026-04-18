from __future__ import annotations

import zipfile

from typing import TYPE_CHECKING

import pytest

from django_spire.contrib.sync.archive.zip import CollisionStrategy, ZipArchive

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def simple_zip(tmp_path: Path) -> Path:
    archive = tmp_path / 'test.zip'

    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('a.txt', 'alpha')
        zf.writestr('b.txt', 'beta')

    return archive


@pytest.fixture
def nested_zip(tmp_path: Path) -> Path:
    archive = tmp_path / 'nested.zip'

    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('dir/a.txt', 'alpha')
        zf.writestr('dir/sub/b.txt', 'beta')

    return archive


@pytest.fixture
def duplicate_zip(tmp_path: Path) -> Path:
    archive = tmp_path / 'dupes.zip'

    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('dir1/same.txt', 'first')
        zf.writestr('dir2/same.txt', 'second')

    return archive


def test_extract_flat(simple_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'out'
    archive = ZipArchive(flatten=True)

    extracted = archive.extract(simple_zip, target)

    assert len(extracted) == 2
    assert (target / 'a.txt').read_text() == 'alpha'
    assert (target / 'b.txt').read_text() == 'beta'


def test_extract_preserves_structure(nested_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'out'
    archive = ZipArchive(flatten=False)

    extracted = archive.extract(nested_zip, target)

    assert len(extracted) == 2
    assert (target / 'dir' / 'a.txt').read_text() == 'alpha'
    assert (target / 'dir' / 'sub' / 'b.txt').read_text() == 'beta'


def test_flatten_collapses_paths(nested_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'out'
    archive = ZipArchive(flatten=True)

    archive.extract(nested_zip, target)

    assert (target / 'a.txt').exists()
    assert (target / 'b.txt').exists()
    assert not (target / 'dir').exists()


def test_collision_raise(duplicate_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'out'
    archive = ZipArchive(flatten=True, collision=CollisionStrategy.RAISE)

    with pytest.raises(FileExistsError, match='Duplicate target'):
        archive.extract(duplicate_zip, target)


def test_collision_skip(duplicate_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'out'
    archive = ZipArchive(flatten=True, collision=CollisionStrategy.SKIP)

    extracted = archive.extract(duplicate_zip, target)

    assert len(extracted) == 1
    assert (target / 'same.txt').read_text() == 'first'


def test_collision_overwrite(duplicate_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'out'
    archive = ZipArchive(flatten=True, collision=CollisionStrategy.OVERWRITE)

    extracted = archive.extract(duplicate_zip, target)

    assert len(extracted) == 2
    assert (target / 'same.txt').read_text() == 'second'


def test_creates_target_dir(simple_zip: Path, tmp_path: Path) -> None:
    target = tmp_path / 'deep' / 'nested' / 'out'
    archive = ZipArchive()

    archive.extract(simple_zip, target)

    assert target.is_dir()


def test_skips_directories(tmp_path: Path) -> None:
    archive_path = tmp_path / 'dirs.zip'

    with zipfile.ZipFile(archive_path, 'w') as zf:
        zf.writestr('file.txt', 'content')
        zf.mkdir('empty_dir/')

    target = tmp_path / 'out'
    archive = ZipArchive(flatten=False)
    extracted = archive.extract(archive_path, target)

    assert len(extracted) == 1


def test_empty_archive(tmp_path: Path) -> None:
    archive_path = tmp_path / 'empty.zip'

    with zipfile.ZipFile(archive_path, 'w'):
        pass

    target = tmp_path / 'out'
    archive = ZipArchive()
    extracted = archive.extract(archive_path, target)

    assert extracted == []


def test_path_traversal_rejected(tmp_path: Path) -> None:
    archive_path = tmp_path / 'evil.zip'

    with zipfile.ZipFile(archive_path, 'w') as zf:
        zf.writestr('../../etc/passwd', 'root:x:0:0')

    target = tmp_path / 'out'
    archive = ZipArchive(flatten=False)

    with pytest.raises(ValueError, match='Path traversal detected'):
        archive.extract(archive_path, target)


def test_path_traversal_safe_when_flattened(tmp_path: Path) -> None:
    archive_path = tmp_path / 'evil.zip'

    with zipfile.ZipFile(archive_path, 'w') as zf:
        zf.writestr('../../etc/passwd', 'root:x:0:0')

    target = tmp_path / 'out'
    archive = ZipArchive(flatten=True)

    extracted = archive.extract(archive_path, target)

    assert len(extracted) == 1
    assert (target / 'passwd').read_text() == 'root:x:0:0'
    assert not (tmp_path.parent / 'etc').exists()
