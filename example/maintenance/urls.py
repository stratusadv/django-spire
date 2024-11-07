from django.urls import path

from example.placeholder import views


app_name = 'placeholder'

urlpatterns = [
    path('<int:pk>/detail', views.placeholder_detail_view, name='detail')
]
