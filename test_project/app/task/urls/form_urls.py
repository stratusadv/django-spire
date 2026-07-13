from django.urls import path

from test_project.app.task.views import form_views

app_name = 'form'

urlpatterns = [
    path('<int:pk>/form/', form_views.form_view, name='form'),
    path('<int:pk>/delete/', form_views.delete_view, name='delete'),
    path('create/modal/', form_views.create_modal_view, name='create_modal'),
    path('<int:pk>/update/modal/', form_views.update_modal_view, name='update_modal'),
    path('<int:pk>/delete/modal/', form_views.delete_modal_view, name='delete_modal'),
]
