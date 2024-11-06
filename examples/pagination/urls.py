from django.urls import path

from examples.pagination import views


app_name = 'pagination'

urlpatterns = [
    path('<int:pk>/detail', views.pagination_detail_view, name='detail')
]
