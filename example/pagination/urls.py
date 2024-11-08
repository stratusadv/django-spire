from django.urls import path

from example.pagination import views


app_name = 'pagination'

urlpatterns = [
    path('', views.pagination_list_view, name='list'),
    path('<int:pk>/detail', views.pagination_detail_view, name='detail')
]
