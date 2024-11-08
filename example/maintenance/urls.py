from django.urls import path

from example.maintenance import views


app_name = 'maintenance'

urlpatterns = [
    path('', views.maintenance_list_view, name='list'),
    path('<int:pk>/detail', views.maintenance_detail_view, name='detail')
]
