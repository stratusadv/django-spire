from django.urls import path

from django_spire.knowledge.collection.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/', page_views.detail_view, name='detail'),
    path('list/', page_views.list_view, name='list'),
]
