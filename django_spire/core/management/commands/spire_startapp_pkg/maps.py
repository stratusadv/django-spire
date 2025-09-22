from __future__ import annotations


def generate_replacement_map(components: list[str]) -> dict[str, str]:
    app_name = components[-1]
    class_name = ''.join(word.title() for word in app_name.split('_'))
    if len(components)> 1:
        parents = components[0:-1]
        parent = components[-2]
    else:
        parents = [app_name,]
        parent = app_name
    module = '.'.join(components)

    return {
        'module': module,
        'spirepermission': parent.lower() + app_name.lower(),
        'SpireChildApp': class_name,
        'SpireChildApps': class_name + 's',
        'spirechildapp': app_name.lower(),
        'spirechildapps': app_name.lower() + 's',
        'spireparentapp': parent.lower(),
        'spireparentapps': parent.lower() + 's',
        'spireReverseFullParentPath': ':'.join(parents[1:]).lower(),
        'spireReverseFullChildPath': ':'.join(parents[1:]).lower() + ':' + app_name.lower(),
        'spireLabelFullChildPath': '_'.join(parents[1:]).lower() + '_' + app_name.lower(),
        'spireTemplateFullChildPath': '/'.join(parents[1:]).lower() + '/' + app_name.lower(),
    }
