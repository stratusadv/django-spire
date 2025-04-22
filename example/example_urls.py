from django.urls import include, path
from django.contrib import admin

app_name = 'example'

urlpatterns = [
    path('', include('example.landing.urls', namespace='landing')),
    path('ai/', include('example.ai.urls', namespace='ai')),
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

urlpatterns += [
    path('spire/ai/', include('django_spire.ai.urls', namespace='spire_ai')),
    path('spire/notification/', include('django_spire.notification.app.urls', namespace='spire_notification')),
    path('spire/permission/', include('django_spire.permission.urls', namespace='spire_permission')),
]

urlpatterns += [
    path('django_glue/', include('django_glue.urls', namespace='django_glue')),
]

urlpatterns += [
    path('admin/', admin.site.urls),
]
