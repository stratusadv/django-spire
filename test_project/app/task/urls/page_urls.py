from django.urls import path

from test_project.app.task.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('children/<int:pk>/', page_views.child_list_view, name='child_list'),
    path('detail/<int:pk>/', page_views.detail_view, name='detail'),
]
