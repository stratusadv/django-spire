from django.urls import path

from test_project.app.activity import views


app_name = 'activity'

urlpatterns = [
    path('', views.demo_view, name='demo'),
    path('create/', views.create_view, name='create'),
    path('child-create/', views.child_create_view, name='child_create'),
    path('unattributed-create/', views.unattributed_create_view, name='unattributed_create'),
    path('update/', views.update_view, name='update'),
    path('soft-delete/', views.soft_delete_view, name='soft_delete'),
    path('restore/', views.restore_view, name='restore'),
    path('hard-delete/', views.hard_delete_view, name='hard_delete'),
    path('cascade-delete/', views.cascade_delete_view, name='cascade_delete'),
    path('bulk-create/', views.bulk_create_view, name='bulk_create'),
    path('bulk-update/', views.bulk_update_view, name='bulk_update'),
    path('queryset-update/', views.queryset_update_view, name='queryset_update'),
    path('queryset-delete/', views.queryset_delete_view, name='queryset_delete'),
    path('member-add/', views.member_add_view, name='member_add'),
    path('member-add-many/', views.member_add_many_view, name='member_add_many'),
    path('member-remove/', views.member_remove_view, name='member_remove'),
    path('member-clear/', views.member_clear_view, name='member_clear'),
    path('reset/', views.reset_view, name='reset'),
]
