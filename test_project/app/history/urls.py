from django.contrib.auth.decorators import login_required
from django.urls import path

from test_project.app.history import views
from test_project.app.history.components import HistoryListComponent


app_name = 'history'

urlpatterns = [
    path('list/', login_required(HistoryListComponent.as_view()), name='list'),
    path('<int:pk>/detail/', views.history_detail_view, name='detail'),
]
