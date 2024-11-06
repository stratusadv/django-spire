from django.urls import path

from examples.comment import views


app_name = 'comment'

urlpatterns = [
    path('<int:pk>/detail', views.comment_detail_view, name='detail')
]
