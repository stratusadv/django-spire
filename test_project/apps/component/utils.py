from pathlib import Path

from django.conf import settings
from django.template import Template, Context


def _read_file(path: Path) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        return '\n' + file.read().strip('\n')


def _render_template(html: str, **context) -> str:
    template = Template(html)
    context = Context(context)
    return template.render(context)


def from_directory(directory: str, **kwargs) ->  dict[str, dict[str, str | Template]]:
    context = {}
    directory = Path(directory)

    exclude_html = kwargs.pop('exclude_html', [])
    exclude_template = kwargs.pop('exclude_template', [])

    for path in directory.rglob('*.html'):
        file = from_file(
            path,
            exclude_html,
            exclude_template,
            **kwargs
        )

        context[path.stem] = file

    return context


def from_file(
    path: str,
    exclude_html: list[str] | None = None,
    exclude_template: list[str] | None = None,
    **kwargs
) -> dict[str, str | Template]:
    if exclude_template is None:
        exclude_template = []

    if exclude_html is None:
        exclude_html = []

    path = Path(settings.BASE_DIR, path)

    html = (
        None
        if path.stem in exclude_html
        else _read_file(path)
    )

    template = (
        None
        if path.stem in exclude_template
        else _render_template(html, **kwargs)
    )

    return {
        'key': path.stem,
        'html': html,
        'template': template
    }
