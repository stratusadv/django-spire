from django.urls import path

from examples.cookbook.views import page_views


app_name = 'cookbook'

urlpatterns = [
    path('<int:pk>/delete/form', page_views.cookbook_delete_view, name='delete'),
    path('<int:pk>/detail', page_views.cookbook_detail_view, name='detail'),
    path('<int:pk>/form', page_views.cookbook_form_view, name='form'),
    path('list/', page_views.cookbook_list_view, name='list'),
]
