from django.urls import include, path

app_name = 'chat'

urlpatterns = [
    path('json/', include('django_spire.ai.chat.urls.json_urls', namespace='json')),
]
