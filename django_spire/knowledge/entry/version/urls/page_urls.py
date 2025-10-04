from django.urls import path

from django_spire.knowledge.entry.version.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
]
