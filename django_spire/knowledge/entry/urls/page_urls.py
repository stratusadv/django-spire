from django.urls import path

from django_spire.knowledge.entry.views import page_views

app_name = 'json'

urlpatterns = [
    path('<int:pk>/delete/', page_views.delete_view, name='delete'),
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
]
