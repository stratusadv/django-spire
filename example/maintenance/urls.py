from django.urls import path

from example.maintenance import views


app_name = 'maintenance'

urlpatterns = [
    path('<int:pk>/detail', views.maintenance_detail_view, name='detail')
]
