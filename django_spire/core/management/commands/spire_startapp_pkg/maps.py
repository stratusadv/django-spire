from __future__ import annotations


def generate_replacement_map(components: list[str]) -> dict[str, str]:
    app_name = components[-1]

    model_name = ''.join(word.title() for word in app_name.split('_'))

    if len(components) > 1:
        parents = components[0:-1]
        parent = components[-2]
    else:
        parents = [app_name]
        parent = app_name

    module = '.'.join(components)

    parent_parts = parents[1:]
    is_root = len(parent_parts) == 0

    if is_root:
        reverse_parent_path = ''
        reverse_path = app_name.lower()
        label_path = app_name.lower()
        template_path = app_name.lower()
    else:
        reverse_parent_path = ':'.join(parent_parts).lower()
        reverse_path = ':'.join(parent_parts).lower() + ':' + app_name.lower()
        label_path = '_'.join(parent_parts).lower() + '_' + app_name.lower()
        template_path = '/'.join(parent_parts).lower() + '/' + app_name.lower()

    # The sequence is important. Plurals must be replaced first;
    # otherwise, it will generate _plural variables and names.
    return {
        'module': module,
        'spire_model_name_plural': model_name + 's',
        'spire_model_name': model_name,
        'spire_app_name_plural': app_name.lower() + 's',
        'spire_app_name': app_name.lower(),
        'spire_parent_app': parent.lower(),
        'spire_reverse_parent_path': reverse_parent_path,
        'spire_reverse_path': reverse_path,
        'spire_label_path': label_path,
        'spire_template_path': template_path,
    }
