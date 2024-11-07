from django.urls import path

from example.home import views


app_name = 'home'

urlpatterns = [
    path('<int:pk>/detail', views.home_detail_view, name='detail')
]
