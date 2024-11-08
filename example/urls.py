from django.contrib import admin
from django.urls import include, path

from example import views


urlpatterns = [
    path('', views.home_page_view, name='home'),
    path('test_model', views.test_model_view, name='test_model')
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('django_glue/', include('django_glue.urls'))
]

urlpatterns += [
    path('authentication/', include('example.authentication.urls', namespace='authentication')),
    # path('authentication_mfa/', include('example.authentication.authentication_mfa.urls', namespace='authentication_mfa')),
    path('breadcrumb/', include('example.breadcrumb.urls', namespace='breadcrumb')),
    path('comment/', include('example.comment.urls', namespace='comment')),
    path('file/', include('example.file.urls', namespace='file')),
    path('form/', include('example.form.urls', namespace='form')),
    path('gamification/', include('example.gamification.urls', namespace='gamification')),
    path('help/', include('example.help.urls', namespace='help')),
    path('history/', include('example.history.urls', namespace='history')),
    path('home/', include('example.home.urls', namespace='home')),
    path('maintenance/', include('example.maintenance.urls', namespace='maintenance')),
    path('notification/', include('example.notification.urls', namespace='notification')),
    path('options/', include('example.options.urls', namespace='options')),
    path('pagination/', include('example.pagination.urls', namespace='pagination')),
    path('permission/', include('example.permission.urls', namespace='permission')),
    path('search/', include('example.search.urls', namespace='search')),
    path('user_account/', include('example.user_account.urls', namespace='user_account')),


    path('component/', include('example.component.urls', namespace='component')),
    path('cookbook/', include('example.cookbook.urls', namespace='cookbook')),
    path('modal/', include('example.modal.urls', namespace='modal'))
]
