from django.urls import path

from example.cookbook import views


app_name = 'cookbook'

urlpatterns = [
    path('<int:pk>/delete/form', views.cookbook_delete_view, name='delete'),
    path('<int:pk>/detail', views.cookbook_detail_view, name='detail'),
    path('<int:pk>/form', views.cookbook_form_view, name='form'),
    path('list/', views.cookbook_list_view, name='list'),
]
