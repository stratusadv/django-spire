from __future__ import annotations


def generate_replacement_map(components: list[str]) -> dict[str, str]:
    app_name = components[-1]
    parent = components[-2] if len(components) > 1 else app_name
    module = '.'.join(components)

    return {
        'module': module,
        'spirepermission': parent.lower() + app_name.lower(),
        'SpireChildApp': app_name.capitalize(),
        'SpireChildApps': app_name.capitalize() + 's',
        'spirechildapp': app_name.lower(),
        'spirechildapps': app_name.lower() + 's',
        'SpireParentApp': parent.capitalize(),
        'SpireParentApps': parent.capitalize() + 's',
        'spireparentapp': parent.lower(),
        'spireparentapps': parent.lower() + 's'
    }
