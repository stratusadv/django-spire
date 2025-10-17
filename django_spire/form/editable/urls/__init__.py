from django.urls.conf import include, path


app_name = 'editable'

urlpatterns = [
    path('json/', include('django_spire.form.editable.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.form.editable.urls.page_urls', namespace='page')),
]
