from django.urls import include, path

app_name = 'help_desk'

urlpatterns = [
    path('page/', include('django_spire.help_desk.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.help_desk.urls.form_urls', namespace='form')),
]