from django.urls import path

from django_spire.ai.chat.views import message_response_views


app_name = 'response'

urlpatterns = [
    path('new/', message_response_views.response_message_render_view, name='new'),
]
