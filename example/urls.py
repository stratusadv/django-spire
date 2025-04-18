from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('example.example_urls', namespace='example')),
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('authentication/', include('django_spire.authentication.urls', namespace='authentication')),
    path('django_glue/', include('django_glue.urls')),
    path('spire/notification/app/', include('django_spire.notification.app.urls', namespace='spire_notification_app')),
    path('spire/ai/', include('django_spire.ai.urls', namespace='spire_ai')),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += [
        *debug_toolbar_urls()
    ]
