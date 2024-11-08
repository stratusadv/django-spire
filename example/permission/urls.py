from django.urls import path

from example.permission import views


app_name = 'permission'

urlpatterns = [
    path('', views.permission_home_view, name='home'),
    path('list/', views.permission_list_view, name='list'),
    path('<int:pk>/detail', views.permission_detail_view, name='detail')
]
