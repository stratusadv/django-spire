from django.urls import path

from django_spire.auth.permissions.decorators import permission_required
from test_project.app.comment import views
from test_project.app.comment.components import CommentListComponent

app_name = 'page'

urlpatterns = [
    path('', views.comment_list_view, name='home'),
    path('list/', views.comment_list_view, name='list'),
    path('<int:pk>/detail/', views.comment_detail_view, name='detail'),
    path('<int:pk>/form/', views.comment_detail_view, name='form'),
    path('list/component/',
         permission_required('project.view_project')(
            CommentListComponent.as_view(),
         ),
         name='list_component'),
]
