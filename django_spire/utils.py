from django.apps import apps


def app_is_installed(app_label: str) -> bool:
    return app_label in list(apps.app_configs.keys())


def check_required_apps(app_label: str) -> None:
    app_config = apps.get_app_config(app_label)
    for required_app_name in app_config.REQUIRED_APPS:
        if not app_is_installed(required_app_name):
            raise Exception(
                f"{app_label} requires {required_app_name} is be in the 'INSTALLED_APPS' list before {app_label} in the django settings module.")
