from django.urls import path

from test_project.apps.notification.views import json_views

app_name = 'json'

urlpatterns = [
    path('test/email', json_views.send_test_email_view, name='test_email'),
]
