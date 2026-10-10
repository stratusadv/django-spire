from django.contrib.auth.decorators import login_required
from django.urls import path

from test_project.app.ordering import views
from test_project.app.ordering.components import DuckListComponent


app_name = 'ordering'

urlpatterns = [
    path('', views.duck_list_view, name='list'),
    path('component/', login_required(DuckListComponent.as_view()), name='list_component'),
    path('<int:pk>/detail/', views.duck_detail_view, name='detail'),
    path('create/', views.duck_create_view, name='create'),
    path('<int:pk>/update/', views.duck_update_view, name='update'),
    path('<int:pk>/delete/', views.duck_delete_view, name='delete'),
    path('<int:pk>/<int:order>/reorder/', views.reorder_view, name='reorder'),
]
