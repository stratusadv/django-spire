from django.urls import include, path
from django.contrib import admin

from django_spire.help_desk.controllers.url_controller import HelpDeskUrlController

app_name = 'example'

urlpatterns = [
    path('', include('test_project.apps.landing.urls', namespace='landing')),
    path('ai/', include('test_project.apps.ai.urls', namespace='ai')),
    path('comment/', include('test_project.apps.comment.urls', namespace='comment')),
    path('help_desk/', HelpDeskUrlController('tacos').url_pattern),
    path('file/', include('test_project.apps.file.urls', namespace='file')),
    path('history/', include('test_project.apps.history.urls', namespace='history')),
    path('home/', include('test_project.apps.home.urls', namespace='home')),
    path('notification/', include('test_project.apps.notification.urls', namespace='notification')),
    path('tabular/', include('test_project.apps.tabular.urls', namespace='tabular')),
    path('wizard/', include('test_project.apps.wizard.urls', namespace='wizard')),
    path('test_model/', include('test_project.apps.test_model.urls', namespace='test_model'))
]

urlpatterns += [
    path('django_glue/', include('django_glue.urls', namespace='django_glue')),
    path('django_spire/', include('django_spire.urls', namespace='django_spire')),
]

urlpatterns += [
    path('admin/', admin.site.urls),
]
