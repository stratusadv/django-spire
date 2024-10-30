from django.urls import path

from django_spire.core import views


app_name = 'core'

urlpatterns = [
    path('search/',
         views.search_view,
         name='search'),
]
