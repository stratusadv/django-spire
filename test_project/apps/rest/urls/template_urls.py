from django.urls import path

from test_project.apps.rest.views import template_views


app_name = 'template'

urlpatterns = [
    path('list/items/', template_views.list_items_view, name='list_items')
]
