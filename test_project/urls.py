import importlib.util

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django_glue import django_glue_urls

from django_spire.shortcuts import django_spire_urls

app_name = 'example'

urlpatterns = [
    path('', include('test_project.app.landing.urls', namespace='landing')),
    path('activity/', include('test_project.app.activity.urls', namespace='activity')),
    path('ai/', include('test_project.app.ai.urls', namespace='ai')),
    path('celery/', include('test_project.app.celery.urls', namespace='celery')),
    path('comment/', include('test_project.app.comment.urls', namespace='comment')),
    path('file/', include('test_project.app.file.urls', namespace='file')),
    path('help_desk/', include('test_project.app.help_desk.urls', namespace='help_desk')),
    path('history/', include('test_project.app.history.urls', namespace='history')),
    path('home/', include('test_project.app.home.urls', namespace='home')),
    path('notification/', include('test_project.app.notification.urls', namespace='notification')),
    path('order/', include('test_project.app.ordering.urls', namespace='order')),
    path('rest/', include('test_project.app.rest.urls', namespace='rest')),
    path('showcase/', include('test_project.app.showcase.urls', namespace='showcase')),
    path('task/', include('test_project.app.task.urls', namespace='task')),
    path('test_model/', include('test_project.app.model_and_service.urls', namespace='test_model')),
    path('auth_sms/', include('test_project.app.auth_sms.urls', namespace='auth_sms')),
]

urlpatterns += django_glue_urls()
urlpatterns += django_spire_urls()

urlpatterns += [path('__dj__/admin/', admin.site.urls)]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if importlib.util.find_spec('django_browser_reload'):
        urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
