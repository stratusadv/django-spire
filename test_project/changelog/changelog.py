from pathlib import Path

from test_project.changelog.parser import parse_changelogs

_DOCS_CHANGELOG_DIR = Path(__file__).resolve().parent.parent.parent / 'docs' / 'changelog'

changelog = parse_changelogs(_DOCS_CHANGELOG_DIR)
