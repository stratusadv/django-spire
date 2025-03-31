from django.apps import apps

def check_required_apps(app_label: str) -> None:
    ac = apps.get_app_config(app_label)
    for required_app_name in ac.REQUIRED_APPS:
        if required_app_name not in list(apps.app_configs.keys()):
            raise Exception(f"{app_label} requires {required_app_name} is be installed in the 'INSTALLED_APPS' list in the django settings module.")
