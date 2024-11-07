from django.urls import path

from example.notification import views


app_name = 'notification'

urlpatterns = [
    path('<int:pk>/detail', views.notification_detail_view, name='detail')
]
