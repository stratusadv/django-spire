from celery.signals import celeryd_after_setup


@celeryd_after_setup.connect
def discover_celery_tasks(sender, instance, **kwargs):
    """
    Custom task discovery to look for specific patterns or avoid errors.
    """
    from django.apps import apps
    import importlib

    for app_name in [config.name for config in apps.get_app_configs()]:
        try:
            module_name = f'{app_name}.celery.tasks'
            importlib.import_module(module_name)
        except ImportError:
            pass
