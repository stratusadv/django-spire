from django.urls import include, path



app_name = 'notification'

# urlpatterns = [
#     path('', page.notification_home_view, name='home'),
#     path('list/', page.notification_list_view, name='list'),
#     path('<int:pk>/detail/', page.notification_detail_view, name='detail')
# ]

urlpatterns = [
    # path('ajax/', include('example.notification.urls.ajax', namespace='page')),
    path('form/', include('example.notification.urls.form', namespace='form')),
    path('page/', include('example.notification.urls.page', namespace='page')),
]
