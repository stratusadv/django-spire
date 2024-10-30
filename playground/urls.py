from django.contrib import admin
from django.urls import path

from playground import views


urlpatterns = [
    path('', views.home_page_view, name='home'),
]

urlpatterns += [
    path('admin/', admin.site.urls),
]
