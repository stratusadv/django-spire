from django.urls import path

from example.history import views


app_name = 'history'

urlpatterns = [
    path('<int:pk>/detail', views.history_detail_view, name='detail')
]
