from django.urls import path

from test_project.apps.notification.views import page_views


app_name = 'page'

urlpatterns = [
    path('', page_views.notification_home_view, name='home'),
    path('list/', page_views.notification_list_view, name='list'),
    path('<int:pk>/detail/', page_views.notification_detail_view, name='detail'),
path('<int:pk>/form/', page_views.notification_form_view, name='form')
]
