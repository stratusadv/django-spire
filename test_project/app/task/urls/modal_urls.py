from django.urls import path

from test_project.app.task.views import modal_views


app_name = 'modal'

urlpatterns = [
    path('<int:pk>/form/', modal_views.form_view, name='form'),
]
