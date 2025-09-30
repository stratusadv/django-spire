from django.apps import AppConfig

from django_spire.utils import check_required_apps


class HelpDeskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_help_desk'
    name = 'django_spire.help_desk'
    MODEL_PERMISSIONS = (
        {
            'name': 'help_desk',
            'verbose_name': 'Help Desk',
            'model_class_path': 'django_spire.help_desk.models.HelpDeskTicket',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.help_desk.urls'
    URLPATTERNS_NAMESPACE = 'help_desk'

    def ready(self) -> None:
        check_required_apps(self.label)
