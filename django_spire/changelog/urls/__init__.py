from django.urls import include, path


app_name = 'changelog'

urlpatterns = [
    path('template/', include('django_spire.contrib.changelog.urls.template_urls', namespace='template')),
]
