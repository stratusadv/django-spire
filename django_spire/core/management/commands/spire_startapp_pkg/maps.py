from __future__ import annotations


def generate_replacement_map(components: list[str]) -> dict[str, str]:
    app_name = components[-1]
    class_name = ''.join(word.title() for word in app_name.split('_'))
    parent = components[-2] if len(components) > 1 else app_name
    module = '.'.join(components)

    return {
        'module': module,
        'spirepermission': parent.lower() + app_name.lower(),
        'SpireChildApp': class_name,
        'SpireChildApps': class_name + 's',
        'spirechildapp': app_name.lower(),
        'spirechildapps': app_name.lower() + 's',
        'SpireParentApp': class_name,
        'SpireParentApps': class_name + 's',
        'spireparentapp': parent.lower(),
        'spireparentapps': parent.lower() + 's'
    }
