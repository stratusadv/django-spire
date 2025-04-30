from django.urls import path, include


app_name = 'landing'

urlpatterns = [
    path('', include('test_project.apps.landing.urls.page_urls', namespace='pages')),
]
