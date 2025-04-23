from django.urls import path, include


app_name = 'group'

urlpatterns = [
    path('', include('django_spire.auth.group.urls.page_urls', namespace='page')),
]
