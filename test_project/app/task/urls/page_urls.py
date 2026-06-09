from django.urls import path

from test_project.app.task.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('detail/<int:pk>/', page_views.detail_view, name='detail'),
]
