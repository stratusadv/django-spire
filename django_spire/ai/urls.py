from django.urls import path

from django_spire.ai import views


app_name = 'ai'

urlpatterns = [
    path(
        'transcribe/',
        views.transcribe_audio,
        name='transcribe'
    )
]
