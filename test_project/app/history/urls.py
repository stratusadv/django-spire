from django.contrib.auth.decorators import login_required
from django.urls import path

from test_project.app.history import views
from test_project.app.history.components import HistoryListComponent


app_name = 'history'

urlpatterns = [
    path('', views.history_home_view, name='home'),
    path('list/', views.history_list_view, name='list'),
    path('list/component/', login_required(HistoryListComponent.as_view()), name='list_component'),
    path('<int:pk>/detail/', views.history_detail_view, name='detail'),
]
