from django.urls import path

from example.home import views


app_name = 'home'

urlpatterns = [
    path('', views.home_home_view, name='home'),
    path('list/', views.home_list_view, name='list'),
    path('<int:pk>/detail/', views.home_detail_view, name='detail')
]
