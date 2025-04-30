from django.urls import path

from test_project.apps.history import views


app_name = 'history'

urlpatterns = [
    path('', views.history_home_view, name='home'),
    path('list/', views.history_list_view, name='list'),
    path('<int:pk>/detail/', views.history_detail_view, name='detail')
]
