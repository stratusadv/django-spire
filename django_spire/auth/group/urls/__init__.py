from django.urls import path, include


app_name = 'group'

urlpatterns = [
    path('page/', include('django_spire.auth.group.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.auth.group.urls.form_urls', namespace='form')),
    path('json/', include('django_spire.auth.group.urls.json_urls', namespace='json')),
]
