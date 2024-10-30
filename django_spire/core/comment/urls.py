from django.urls import path

from django_spire.core.comment import views


app_name = 'comment'

urlpatterns = [
    path('<int:comment_pk>/<int:obj_pk>/<str:app_label>/<str:model_name>/form/content/',
         views.comment_modal_form_content,
         name='form_content'),

    path('<int:comment_pk>/<int:obj_pk>/<str:app_label>/<str:model_name>/form/',
         views.comment_form_view,
         name='form'),

    path('<int:comment_pk>/<int:obj_pk>/<str:app_label>/<str:model_name>/delete/form/',
         views.comment_modal_delete_form_view,
         name='delete_form'),
]
