from django.urls import path

from test_project.app.auth_sms.views import page_views

app_name = 'page'

urlpatterns = [path('', page_views.phone_verification_view, name='phone_verification')]
