from django.urls import path

from examples.search import views


app_name = 'search'

urlpatterns = [
    path('<int:pk>/detail', views.search_detail_view, name='detail')
]
