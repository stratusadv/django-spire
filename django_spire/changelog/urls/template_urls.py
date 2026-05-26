from django.urls import path

from django_spire.changelog.views import template_views


app_name = 'template'

urlpatterns = [
    path('rows/', template_views.changelog_rows_view, name='rows'),
]
