from django.urls import include, path

app_name = 'auth'

urlpatterns = [
    path('', include('django_spire.auth.urls.admin_urls', namespace='admin')),
    path('redirect/', include('django_spire.auth.urls.redirect_urls', namespace='redirect')),
    path('mfa/', include('django_spire.auth.mfa.urls', namespace='mfa')),
    path('sms/', include('django_spire.auth.sms.urls', namespace='sms')),
    path('user/', include('django_spire.auth.user.urls', namespace='user')),
    path('group/', include('django_spire.auth.group.urls', namespace='group')),
]
