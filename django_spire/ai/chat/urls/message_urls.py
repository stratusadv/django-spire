from django.urls import include, path

from django_spire.ai.chat.views import message_views


app_name = 'message'

urlpatterns = [
    path('request/', include('django_spire.ai.chat.urls.message_request_urls', namespace='request')),
    path('response/', include('django_spire.ai.chat.urls.message_response_urls', namespace='response')),
]

urlpatterns += [
    path('load/chat/<int:chat_id>/', message_views.load_messages_render_view, name='load_chat'),
]

