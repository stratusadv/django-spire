from django.urls import path

from test_project.apps.comment import views


app_name = 'page'

urlpatterns = [
    path('', views.comment_list_view, name='home'),
    path('list/', views.comment_list_view, name='list'),
    path('<int:pk>/detail/', views.comment_detail_view, name='detail'),
    path('<int:pk>/form/', views.comment_detail_view, name='form')
]
