import importlib.util

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django_glue import django_glue_urls

app_name = 'example'

urlpatterns = [
    path('', include('test_project.app.landing.urls', namespace='landing')),
    path('ai/', include('test_project.app.ai.urls', namespace='ai')),
    path('celery/', include('test_project.app.celery.urls', namespace='celery')),
    path('comment/', include('test_project.app.comment.urls', namespace='comment')),
    path('file/', include('test_project.app.file.urls', namespace='file')),
    path('help_desk/', include('test_project.app.help_desk.urls', namespace='help_desk')),
    path('history/', include('test_project.app.history.urls', namespace='history')),
    path('home/', include('test_project.app.home.urls', namespace='home')),
    path(
        'infinite_scrolling/',
        include('test_project.app.infinite_scrolling.urls', namespace='infinite_scrolling'),
    ),
    path('notification/', include('test_project.app.notification.urls', namespace='notification')),
    path('order/', include('test_project.app.ordering.urls', namespace='order')),
    path(
        'queryset-filtering/',
        include('test_project.app.queryset_filtering.urls', namespace='queryset_filtering'),
    ),
    path('rest/', include('test_project.app.rest.urls', namespace='rest')),
    path('sync/', include('test_project.app.sync.urls', namespace='sync')),
    path('test_model/', include('test_project.app.model_and_service.urls', namespace='test_model')),
    path('theme/', include('django_spire.theme.urls', namespace='theme')),
]

urlpatterns += [path('ds/', include('django_spire.urls', namespace='django_spire'))]

urlpatterns += django_glue_urls()

urlpatterns += [path('admin/', admin.site.urls)]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if importlib.util.find_spec('debug_toolbar'):
        import debug_toolbar

        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

    if importlib.util.find_spec('django_browser_reload'):
        urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
