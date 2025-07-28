from django.urls.conf import path, include


app_name = 'spirechildapp'

urlpatterns = [
    path('', include('module.page_urls', namespace='page')),
    path('', include('module.form_urls', namespace='form')),
]
