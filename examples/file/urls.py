from django.urls import path

from examples.file import views


app_name = 'file'

urlpatterns = [
    path('<int:pk>/detail', views.file_detail_view, name='detail')
]
