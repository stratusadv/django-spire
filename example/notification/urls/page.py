from django.urls import path

from example.notification.views import page


app_name = 'page'

urlpatterns = [
    path('', page.notification_home_view, name='home'),
    path('list/', page.notification_list_view, name='list'),
    path('<int:pk>/detail/', page.notification_detail_view, name='detail')
]