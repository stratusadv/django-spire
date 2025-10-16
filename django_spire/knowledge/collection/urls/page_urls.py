from django.urls import path

from django_spire.knowledge.collection.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/delete/', page_views.delete_view, name='delete'),
]
