from django.urls import include, path

app_name = 'auth_sms'

urlpatterns = [path('', include('test_project.app.auth_sms.urls.page_urls', namespace='page'))]
