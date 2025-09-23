from __future__ import annotations


def generate_replacement_map(components: list[str]) -> dict[str, str]:
    app_name = components[-1]
    model_name = ''.join(word.title() for word in app_name.split('_'))
    if len(components)> 1:
        parents = components[0:-1]
        parent = components[-2]
    else:
        parents = [app_name,]
        parent = app_name
    module = '.'.join(components)

    return {
        'module': module,
        'spire_model_name': model_name,
        'spire_model_names': model_name + 's',
        'spire_app_name': app_name.lower(),
        'spire_app_names': app_name.lower() + 's',
        'spire_parent_app': parent.lower(),
        'spire_parent_apps': parent.lower() + 's',
        'spire_reverse_parent_path': ':'.join(parents[1:]).lower(),
        'spire_reverse_path': ':'.join(parents[1:]).lower() + ':' + app_name.lower(),
        'spire_label_path': '_'.join(parents[1:]).lower() + '_' + app_name.lower(),
        'spire_template_path': '/'.join(parents[1:]).lower() + '/' + app_name.lower(),
    }
