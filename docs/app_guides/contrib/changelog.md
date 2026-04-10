# Changelog

> **Purpose:** Provide a structured, version-tracked changelog that surfaces your latest application updates to users directly inside the UI via an infinite-scrolling card component.

---

## Why Changelog?

Keeping users informed about what has changed in your application builds trust and reduces support requests. **The Changelog app** makes this easy by:

- Defining changelog entries as simple Python dataclasses — no database required
- Automatically parsing your existing `changelog.md` and `archived_changelog.md` markdown files
- Rendering entries in an infinite-scrolling card that can be dropped anywhere in your project
- Grouping changes by version, type, and affected app

---

## Quick Start

### 1. Add to Installed Apps

```python
# base_settings.py
INSTALLED_APPS = [
    ...
    'django_spire.contrib.changelog',
    ...
]
```

### 2. Point the Setting to Your Changelog Module

```python
# base_settings.py
DJANGO_SPIRE_CHANGELOG_MODULE = 'app.home.changelog.changelog'
```

This is a dotted Python import path. The last segment is the attribute name that gets retrieved from the module — so `'app.home.changelog.changelog'` imports the `app.home` module and reads its `changelog` attribute.

### 3. Create Your Changelog File

Create the file that the setting points to and define a `changelog` list:

```python
# app/home/changelog.py
from datetime import date

from django_spire.contrib.changelog import Change, ChangelogEntry, ChangeLogTypeChoices

changelog = [
    ChangelogEntry(
        version='0.9.0',
        date=date(2026, 3, 11),
        type=ChangeLogTypeChoices.FEATURE,
        changes=[
            Change(
                app='Changelog',
                description='Added changelog to keep up with latest updates',
            ),
            Change(
                app='Location',
                description='Updated model to include client feedback',
            ),
        ],
    ),
    ChangelogEntry(
        version='0.8.2',
        date=date(2026, 2, 14),
        type=ChangeLogTypeChoices.BUG_FIX,
        changes=[
            Change(
                app='Notifications',
                description='Fixed duplicate notification bug on page reload',
            ),
        ],
    ),
]
```

The list is ordered **most recent first** (top to bottom).

### 4. Include the Card

Drop the changelog card anywhere in your templates:

```html
{ include 'django_spire/contrib/changelog/card/changelog_card.html' }
```

That's it — the card lazy-loads entries with infinite scroll, 20 at a time.

---

## Core Concepts

### `ChangelogEntry`

Represents a single version release. Every entry in your `changelog` list must be a `ChangelogEntry`.

```python
@dataclass
class ChangelogEntry:
    version: str              # Version string, e.g. '1.4.2'
    date: date                # Release date
    type: ChangeLogTypeChoices  # Primary type of this release
    changes: list[Change]     # List of individual changes in this release
```

### `Change`

Represents a single line item within a release. Each `Change` belongs to a specific area of your application.

```python
@dataclass
class Change:
    app: str          # Name of the app or area affected, e.g. 'Notifications'
    description: str  # Plain-English description of what changed
```

### `ChangeLogTypeChoices`

A `TextChoices` enum that classifies each release. Use the value that best describes the primary nature of the release.

| Choice | Value | Label | When to use |
|---|---|---|---|
| `ChangeLogTypeChoices.FEATURE` | `'feat'` | Feature | New functionality added |
| `ChangeLogTypeChoices.BUG_FIX` | `'bug'` | Bug Fix | Defects corrected |
| `ChangeLogTypeChoices.CHANGE` | `'chan'` | Change | Improvements, refactors, or breaking changes |

---

## Parsing from Markdown Files (Optional)

If your project already maintains `changelog.md` and `archived_changelog.md` files, you can parse them automatically instead of hand-writing entries.

Create a parser module and call it from your changelog file:

```python
# app/home/changelog.py
from pathlib import Path

from app.home.changelog.changelog_parser import parse_changelogs

_DOCS_CHANGELOG_DIR = Path(__file__).resolve().parent.parent.parent / 'docs' / 'changelog'

changelog = parse_changelogs(_DOCS_CHANGELOG_DIR)
```

```python
# app/home/changelog_parser.py
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


def parse_changelogs(docs_changelog_dir: Path) -> list[ChangelogEntry]:
    """Parse changelog.md and archived_changelog.md into ChangelogEntry objects.

    Entries from changelog.md appear first (most recent), followed by
    archived_changelog.md.
    """
    changelog_file = docs_changelog_dir / 'changelog.md'
    archived_file = docs_changelog_dir / 'archived_changelog.md'

    entries: list[ChangelogEntry] = []

    if changelog_file.exists():
        entries.extend(_parse_md_file(changelog_file))

    if archived_file.exists():
        entries.extend(_parse_md_file(archived_file))

    return entries
```

The parser expects the standard heading structure used in Django Spire's own changelog files:

```markdown
## v1.2.0

### Features
- Added something new

### Fixes
- Fixed a bug
```

Each `## vX.X.X` heading becomes one `ChangelogEntry`. The primary `ChangeLogTypeChoices` is determined by the highest-priority section present in that version block (`FEATURE > BUG_FIX > CHANGE`). Each bullet point under a section heading becomes a `Change`, with the section name used as the `app`.

!!! note

    Dates are not stored in markdown changelog files. When parsing from markdown, `date.today()` is used as a placeholder for all entries.

---

## API Reference

### `ChangelogEntry`

```python
ChangelogEntry(
    version: str,
    date: date,
    type: ChangeLogTypeChoices,
    changes: list[Change],
)
```

### `Change`

```python
Change(
    app: str,
    description: str,
)
```

### `ChangeLogTypeChoices`

```python
from django_spire.contrib.changelog import ChangeLogTypeChoices

ChangeLogTypeChoices.FEATURE  # 'feat' - Feature
ChangeLogTypeChoices.BUG_FIX  # 'bug'  - Bug Fix
ChangeLogTypeChoices.CHANGE   # 'chan' - Change
```

### Template Card

```html
{ include 'django_spire/contrib/changelog/card/changelog_card.html' }
```

Renders a `300px` infinite-scrolling card that loads 20 entries per page. No context variables required — the card fetches its own data.

---

## Settings Reference

| Setting | Type | Description |
|---|---|---|
| `DJANGO_SPIRE_CHANGELOG_MODULE` | `str` | Dotted Python path to the `changelog` list attribute |

```python
# base_settings.py
DJANGO_SPIRE_CHANGELOG_MODULE = 'app.home.changelog.changelog'
```
