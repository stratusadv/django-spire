from django.urls import path

from django_spire.ai.chat.views import message_request_views


app_name = 'request'

urlpatterns = [
    path('new/', message_request_views.request_message_render_view, name='new'),
]
