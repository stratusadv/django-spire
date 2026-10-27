from django.contrib.auth.decorators import login_required
from django.urls import path

from test_project.app.task.components import TaskListComponent
from test_project.app.task.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', login_required(TaskListComponent.as_view()), name='list'),
    path('detail/<int:pk>/', page_views.detail_view, name='detail'),
]
