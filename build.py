from __future__ import annotations

from pathlib import Path

import libsass


def compile_scss_to_css(scss_file: Path, css_file: Path) -> None:
    with open(scss_file, 'r', encoding='utf-8') as f:
        scss_content = f.read()

    css_content = libsass.compile(
        string=scss_content,
        output_style='compressed',
        include_paths=[str(scss_file.parent)]
    )

    css_file.parent.mkdir(parents=True, exist_ok=True)

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)


def auto_compile_all_scss() -> None:
    base_dir = Path(__file__).resolve().parent
    scss_dir = base_dir / 'django_spire' / 'core' / 'static' / 'django_spire' / 'scss'
    css_dir = base_dir / 'django_spire' / 'core' / 'static' / 'django_spire' / 'css'

    if not scss_dir.exists():
        return

    for scss_file in scss_dir.glob('*.scss'):
        if scss_file.name.startswith('_'):
            continue

        css_file = css_dir / scss_file.name.replace('.scss', '.css')

        if not css_file.exists() or scss_file.stat().st_mtime > css_file.stat().st_mtime:
            compile_scss_to_css(scss_file, css_file)
