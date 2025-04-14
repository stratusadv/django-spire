from django.urls import path

from django_spire.ai.chat.views import render_views


app_name = 'render'

urlpatterns = [
    path('<int:chat_id>/load/messages/', render_views.load_messages_render_view, name='load_messages'),
    path('request/message/', render_views.request_message_render_view, name='request_message'),
    path('response/message/', render_views.response_message_render_view, name='response_message'),
]
