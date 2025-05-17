from django.urls import include, path

app_name = 'chat'

urlpatterns = [
    path('json/', include('django_spire.ai.chat.urls.json_urls', namespace='json')),
    path('message/', include('django_spire.ai.chat.urls.message_urls', namespace='message')),
    path('template/', include('django_spire.ai.chat.urls.template_urls', namespace='template')),
]
