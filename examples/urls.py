from django.contrib import admin
from django.urls import include, path

from examples import views


urlpatterns = [
    path('', views.home_page_view, name='home'),
    path('test_model', views.test_model_view, name='test_model')
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('django_glue/', include('django_glue.urls'))
]

urlpatterns += [
    path('authentication/', include('django_spire.authentication.urls', namespace='authentication')),
    path('user_account/', include('django_spire.user_account.urls', namespace='user_account')),
]

urlpatterns += [
    path('component/', include('examples.component.urls', namespace='component')),
    path('cookbook/', include('examples.cookbook.urls.page_urls', namespace='cookbook')),
    path('modal/', include('examples.modal.urls', namespace='modal'))
]
