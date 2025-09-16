from django.urls import path

from django_spire.theme.views import ajax_views

app_name = 'ajax'

urlpatterns = [
    path('get_config/', ajax_views.get_config, name='get_config'),
    path('set_theme/', ajax_views.set_theme, name='set_theme'),
]
