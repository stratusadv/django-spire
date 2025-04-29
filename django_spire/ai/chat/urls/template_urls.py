from django.urls import path

from django_spire.ai.chat.views import template_views


app_name = 'template'

urlpatterns = [
    path('load/', template_views.load_chat_view, name='load'),
    path('recent/', template_views.recent_chat_list_view, name='recent'),
    path('search/', template_views.search_chat_view, name='search'),
]
