from pathlib import Path

from django.template import Template, Context


def _read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return '\n' + file.read().strip('\n')


def _render_template(html, **context):
    template = Template(html)
    context = Context(context)
    return template.render(context)


def from_directory(directory, **kwargs):
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


def from_file(path, exclude_html = [], exclude_template = [], **kwargs):
    path = Path(path)

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
