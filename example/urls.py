from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from example import views


urlpatterns = [
    path('', views.example_page_view, name='home')
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('django_glue/', include('django_glue.urls')),
]

urlpatterns += [
    path('authentication/', include('example.authentication.urls', namespace='authentication')),
    path('breadcrumb/', include('example.breadcrumb.urls', namespace='breadcrumb')),
    path('comment/', include('example.comment.urls', namespace='comment')),
    path('file/', include('example.file.urls', namespace='file')),
    path('form/', include('example.form.urls', namespace='form')),
    path('gamification/', include('example.gamification.urls', namespace='gamification')),
    path('help/', include('example.help.urls', namespace='help')),
    path('history/', include('example.history.urls', namespace='history')),
    path('home/', include('example.home.urls', namespace='home')),
    path('maintenance/', include('example.maintenance.urls', namespace='maintenance')),
    path('modal/', include('example.modal.urls', namespace='modal')),
    path('notification/', include('example.notification.urls', namespace='notification')),
    path('options/', include('example.options.urls', namespace='options')),
    path('pagination/', include('example.pagination.urls', namespace='pagination')),
    path('permission/', include('example.permission.urls', namespace='permission')),
    path('search/', include('example.search.urls', namespace='search')),
    path('speech_to_text/', include('example.speech_to_text.urls', namespace='speech_to_text')),
    path('tabular/', include('example.tabular.urls', namespace='tabular')),
    path('user_account/', include('example.user_account.urls', namespace='user_account')),
    path('wizard/', include('example.wizard.urls', namespace='wizard')),

    path('component/', include('example.component.urls', namespace='component')),
    path('cookbook/', include('example.cookbook.urls', namespace='cookbook')),
    path('test_model/', include('example.test_model.urls', namespace='test_model'))
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += [
        *debug_toolbar_urls()
    ]
