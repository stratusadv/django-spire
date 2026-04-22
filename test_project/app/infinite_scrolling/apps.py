from django.apps import AppConfig


class InfiniteScrollingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'infinite_scrolling'
    name = 'test_project.apps.infinite_scrolling'

    MODEL_PERMISSIONS = (
        {
            'name': 'infinite_scrolling',
            'model_class_path': 'test_project.apps.infinite_scrolling.models.InfiniteScrolling',
            'is_proxy_model': False
        },
    )
