from django.urls import path

from django_spire.speech_to_text import views


app_name = 'speech_to_text'

urlpatterns = [
    path(
        'transcribe/',
        views.transcribe_audio,
        name='transcribe'
    )
]
