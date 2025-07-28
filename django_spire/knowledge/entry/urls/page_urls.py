from django.urls import path

from django_spire.knowledge.entry.views import page_views

app_name = 'json'

urlpatterns = [
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
]
