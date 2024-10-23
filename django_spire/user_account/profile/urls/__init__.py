from django.urls import path, include

app_name = '__init__'
urlpatterns = [
    path('page/', include('app.user_account.profile.urls.page_urls', namespace='page')),
]