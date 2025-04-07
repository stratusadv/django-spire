from django.apps import AppConfig


class SpeechToTextConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_speech_to_text'
    name = 'django_spire.speech_to_text'
