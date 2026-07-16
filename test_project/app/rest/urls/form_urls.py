from django.urls import path

from test_project.app.rest.views import form_views

app_name = 'form'

urlpatterns = [
    path('<int:pk>/form/', form_views.form_view, name='form'),
    path('<int:pk>/delete/', form_views.delete_view, name='delete'),
    path('<int:pk>/glue/', form_views.glue_form_view, name='glue'),
]
