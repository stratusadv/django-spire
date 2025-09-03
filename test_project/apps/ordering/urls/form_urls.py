from django.urls import path

from test_project.apps.ordering.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_form_view, name='create'),
    path('<int:pk>/delete/form/modal/', form_views.delete_form_modal_view, name='delete_form_modal'),
    path('<int:pk>/form/content/', form_views.form_content_modal_view, name='form_modal_content'),
    path('<int:pk>/form/', form_views.form_view, name='form'),
]
