from django.urls import include, path


app_name = '__init__'

urlpatterns = [
    path('page/', include('django_spire.user_account.profile.urls.page_urls', namespace='page')),
]
