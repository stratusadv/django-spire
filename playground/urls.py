from django.contrib import admin
from django.urls import include, path

from playground import views


urlpatterns = [
    path('', views.home_page_view, name='home'),
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('django_glue/', include('django_glue.urls')),
    path('user_account/', include('django_spire.user_account.urls', namespace='user_account')),
    path('test_model', views.test_model_view, name='test_model'),
]
