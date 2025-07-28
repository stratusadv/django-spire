from django.urls.conf import path, include


app_name = 'spirechildapp'

urlpatterns = [
    path('page/', include('module.page_urls', namespace='page')),
    path('form/', include('module.form_urls', namespace='form')),
]
