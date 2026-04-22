from django.urls import path, include


app_name = 'landing'

urlpatterns = [
    path('', include('test_project.app.landing.urls.page_urls', namespace='pages')),
]
