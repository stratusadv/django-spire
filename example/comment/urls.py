from django.urls import path

from example.comment import views


app_name = 'comment'

urlpatterns = [
    path('', views.comment_list_view, name='list'),
    path('<int:pk>/detail', views.comment_detail_view, name='detail')
]
