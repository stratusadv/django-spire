from django.apps import apps


def app_is_installed(app_label: str) -> bool:
    return app_label in list(apps.app_configs.keys())


def check_required_apps(app_label: str) -> None:
    app_config = apps.get_app_config(app_label)
    for required_app_name in app_config.REQUIRED_APPS:
        if not app_is_installed(required_app_name):
            raise Exception(
                f"{app_label} requires {required_app_name} is be in the 'INSTALLED_APPS' list before {app_label} in the django settings module.")


def get_class_from_string(class_string: str) -> type:
    class_parts = class_string.split('.')

    if len(class_parts) < 2:
        raise Exception(f"Class string {class_string} is not a valid class string.")

    module_path = '.'.join(class_parts[:-1])
    class_name = class_parts[-1]

    module = __import__(module_path, fromlist=[class_name])

    return getattr(module, class_name)


def get_class_name_from_class(cls: type) -> str:
    return cls.__module__ + '.' + cls.__qualname__