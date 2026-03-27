from __future__ import annotations

import re

from datetime import date
from pathlib import Path

from django_spire.contrib.changelog import Change, ChangelogEntry, ChangeLogTypeChoices


_SECTION_TYPE_MAP: dict[str, ChangeLogTypeChoices] = {
    'features': ChangeLogTypeChoices.FEATURE,
    'feature': ChangeLogTypeChoices.FEATURE,
    'fixes': ChangeLogTypeChoices.BUG_FIX,
    'fix': ChangeLogTypeChoices.BUG_FIX,
    'changes': ChangeLogTypeChoices.CHANGE,
    'change': ChangeLogTypeChoices.CHANGE,
    'breaking': ChangeLogTypeChoices.CHANGE,
    'tools': ChangeLogTypeChoices.CHANGE,
}

_TYPE_PRIORITY: dict[ChangeLogTypeChoices, int] = {
    ChangeLogTypeChoices.FEATURE: 2,
    ChangeLogTypeChoices.BUG_FIX: 1,
    ChangeLogTypeChoices.CHANGE: 0,
}

_VERSION_PATTERN = re.compile(r'^## [vV](\S+)', re.MULTILINE)
_SECTION_PATTERN = re.compile(r'^### (.+)$', re.MULTILINE)
_CODE_FENCE_PATTERN = re.compile(r'^```', re.MULTILINE)
_INLINE_CODE_PATTERN = re.compile(r'`([^`]*)`')


def _strip_inline_code(text: str) -> str:
    return _INLINE_CODE_PATTERN.sub(r'\1', text)


def _strip_code_blocks(text: str) -> str:
    parts = _CODE_FENCE_PATTERN.split(text)
    return ''.join(parts[i] for i in range(0, len(parts), 2))


def _parse_md_file(file_path: Path) -> list[ChangelogEntry]:
    entries = []

    content = file_path.read_text(encoding='utf-8')
    version_matches = list(_VERSION_PATTERN.finditer(content))

    for i, version_match in enumerate(version_matches):
        version = version_match.group(1).strip()

        block_start = version_match.end()
        block_end = version_matches[i + 1].start() if i + 1 < len(version_matches) else len(content)
        block = _strip_code_blocks(content[block_start:block_end])

        section_matches = list(_SECTION_PATTERN.finditer(block))

        changes: list[Change] = []
        primary_type = ChangeLogTypeChoices.CHANGE

        for j, section_match in enumerate(section_matches):
            section_name = section_match.group(1).strip()
            section_type = _SECTION_TYPE_MAP.get(section_name.lower(), ChangeLogTypeChoices.CHANGE)

            if _TYPE_PRIORITY.get(section_type, 0) > _TYPE_PRIORITY.get(primary_type, 0):
                primary_type = section_type

            section_start = section_match.end()
            section_end = section_matches[j + 1].start() if j + 1 < len(section_matches) else len(block)
            section_content = block[section_start:section_end]

            for line in section_content.splitlines():
                stripped = line.strip()

                if not stripped.startswith('- '):
                    continue

                if line.startswith('  ') or line.startswith('\t'):
                    continue

                description = _strip_inline_code(stripped[2:].strip())

                if description:
                    changes.append(Change(app=section_name, description=description))

        entries.append(ChangelogEntry(
            version=version,
            date=date.today(),
            type=primary_type,
            changes=changes,
        ))

    return entries


def parse_changelogs(docs_changelog_dir: Path) -> list[ChangelogEntry]:
    changelog_file = docs_changelog_dir / 'changelog.md'
    archived_file = docs_changelog_dir / 'archived_changelog.md'

    entries: list[ChangelogEntry] = []

    if changelog_file.exists():
        entries.extend(_parse_md_file(changelog_file))

    if archived_file.exists():
        entries.extend(_parse_md_file(archived_file))

    return entries
