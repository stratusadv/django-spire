from django.urls import path

from example.help import views


app_name = 'help'

urlpatterns = [
    path('', views.help_home_view, name='home'),
    path('list/', views.help_list_view, name='list'),
    path('<int:pk>/detail/', views.help_detail_view, name='detail')
]
