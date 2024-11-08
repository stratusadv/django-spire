from django.urls import path

from example.notification import views


app_name = 'notification'

urlpatterns = [
    path('', views.notification_home_view, name='home'),
    path('list/', views.notification_list_view, name='list'),
    path('<int:pk>/detail/', views.notification_detail_view, name='detail')
]
