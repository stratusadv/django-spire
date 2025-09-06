from django.apps import AppConfig

from django_spire.utils import check_required_apps


class UserAccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_auth_user'
    name = 'django_spire.auth.user'

    MODEL_PERMISSIONS = (
        {
            'name': 'user',
            'model_class_path': 'django_spire.auth.user.models.AuthUser',
            'is_proxy_model': True
        },
    )

    REQUIRED_APPS = ('django_spire_core', 'django_spire_auth')

    def ready(self) -> None:
        check_required_apps(self.label)
