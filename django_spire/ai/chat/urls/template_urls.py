from django.urls import path

from django_spire.ai.chat.views import template_views


app_name = 'template'

urlpatterns = [
    path('load/', template_views.load_template_view, name='load'),
    path('recent/', template_views.recent_template_view, name='recent'),
    path('search/', template_views.search_template_view, name='search'),
]
