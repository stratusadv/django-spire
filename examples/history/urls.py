from django.urls import path

from examples.history import views


app_name = 'history'

urlpatterns = [
    path('<int:pk>/detail', views.history_detail_view, name='detail')
]
