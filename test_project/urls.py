import importlib.util

from django.conf import settings
from django.contrib import admin
from django.urls import include, path


app_name = 'example'

urlpatterns = [
    path('', include('test_project.apps.landing.urls', namespace='landing')),
    path('ai/', include('test_project.apps.ai.urls', namespace='ai')),
    path('comment/', include('test_project.apps.comment.urls', namespace='comment')),
    path('help_desk/', include('test_project.apps.help_desk.urls', namespace='help_desk')),
    path('file/', include('test_project.apps.file.urls', namespace='file')),
    path('history/', include('test_project.apps.history.urls', namespace='history')),
    path('home/', include('test_project.apps.home.urls', namespace='home')),
    path('notification/', include('test_project.apps.notification.urls', namespace='notification')),
    path('order/', include('test_project.apps.ordering.urls', namespace='order')),
    path('tabular/', include('test_project.apps.tabular.urls', namespace='tabular')),
    path('test_model/', include('test_project.apps.model_and_service.urls', namespace='test_model')),
    path('theme/', include('django_spire.theme.urls', namespace='theme')),
    path('queryset-filtering/', include('test_project.apps.queryset_filtering.urls', namespace='queryset_filtering')),
    path('wizard/', include('test_project.apps.wizard.urls', namespace='wizard')),
]

urlpatterns += [
    path('django_glue/', include('django_glue.urls', namespace='django_glue')),
    path('django_spire/', include('django_spire.urls', namespace='django_spire')),
]

urlpatterns += [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    if importlib.util.find_spec('debug_toolbar'):
        import debug_toolbar

        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]

    if importlib.util.find_spec('django_browser_reload'):
        urlpatterns += [
            path('__reload__/', include('django_browser_reload.urls')),
        ]

