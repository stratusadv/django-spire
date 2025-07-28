from django.urls import path

from django_spire.knowledge.entry.editor.views import page_views

app_name = 'page'

urlpatterns = [
    path('edit/<int:pk>/', page_views.edit_view, name='edit'),
]
