from django.urls import path

from test_project.apps.notification.views import form_views

app_name = 'form'

urlpatterns = [
    path('<int:pk>/form/', form_views.notification_form_view, name='update')
]
