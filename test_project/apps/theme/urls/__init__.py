from django.urls.conf import path, include


app_name = 'theme'

urlpatterns = [
    path('page/', include('test_project.apps.theme.urls.page_urls', namespace='page')),
    path('form/', include('test_project.apps.theme.urls.form_urls', namespace='form')),
]
