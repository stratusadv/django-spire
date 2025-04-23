from django.apps import AppConfig

from django_spire.utils import check_required_apps


class SpeechToTextConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_speech_to_text'
    name = 'django_spire.speech_to_text'

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.speech_to_text.urls'
    URLPATTERNS_NAMESPACE = 'speech_to_text'

    def ready(self) -> None:
        check_required_apps(self.label)
