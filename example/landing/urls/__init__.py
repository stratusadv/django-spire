from django.urls import path, include


app_name = 'landing'

urlpatterns = [
    path('', include('example.landing.urls.page_urls', namespace='pages')),
]
