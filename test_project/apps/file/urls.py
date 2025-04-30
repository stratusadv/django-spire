from django.urls import path

from test_project.apps.file import views


app_name = 'file'

urlpatterns = [
    path('', views.file_home_view, name='home'),
    path('list/', views.file_list_view, name='list'),
    path('<int:pk>/detail/', views.file_detail_view, name='detail')
]
