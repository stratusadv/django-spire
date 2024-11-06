from django.urls import path

from examples.placeholder import views


app_name = 'placeholder'

urlpatterns = [
    path('<int:pk>/detail', views.placeholder_detail_view, name='detail')
]
