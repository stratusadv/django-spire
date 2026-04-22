from django.apps import AppConfig


class LazyTabsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'lazy_tabs'
    name = 'test_project.apps.lazy_tabs'

    MODEL_PERMISSIONS = (
        {
            'name': 'lazy_tabs',
            'model_class_path': 'test_project.apps.lazy_tabs.models.LazyTabs',
            'is_proxy_model': False
        },
    )
