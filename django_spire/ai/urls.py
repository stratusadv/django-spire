from django.urls import include, path

app_name = 'spire_ai'

urlpatterns = [
    path('chat/', include('django_spire.ai.chat.urls', namespace='chat')),
]
