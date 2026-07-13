from django.urls import path, include

app_name = 'rest'

urlpatterns = [
    path('page/', include('test_project.app.rest.urls.page_urls')),
    path('form/', include('test_project.app.rest.urls.form_urls')),
]
