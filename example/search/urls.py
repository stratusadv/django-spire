from django.urls import path

from example.search import views


app_name = 'search'

urlpatterns = [
    path('', views.search_list_view, name='list'),
    path('<int:pk>/detail', views.search_detail_view, name='detail')
]
