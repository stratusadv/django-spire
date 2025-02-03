from django.urls import path

from app.parent.placeholder import views


app_name = 'placeholder'

urlpatterns = [
    path('<int:pk>/delete/form', views.placeholder_delete_view, name='delete'),
    path('<int:pk>/detail', views.placeholder_detail_view, name='detail'),
    path('<int:pk>/form/content', views.placeholder_form_content_view, name='form'),
    path('<int:pk>/form', views.placeholder_form_view, name='form'),
    path('list/', views.placeholder_list_view, name='list'),
]
