from django.urls import path, include

app_name = '__init__'
urlpatterns  = [
    path('', include('app.user_account.authentication.mfa.urls.page_urls', namespace='page')),
    path('', include('app.user_account.authentication.mfa.urls.redirect_urls', namespace='redirect')),
]
