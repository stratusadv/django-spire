from django.urls import path

from examples.permission import views


app_name = 'permission'

urlpatterns = [
    path('<int:pk>/detail', views.permission_detail_view, name='detail')
]
