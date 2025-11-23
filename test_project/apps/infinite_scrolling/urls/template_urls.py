from django.urls import path

from test_project.apps.infinite_scrolling.views import template_views


app_name = 'template'

urlpatterns = [
    path('items/', template_views.items_view, name='items'),
    path('rows/', template_views.rows_view, name='rows'),
]
