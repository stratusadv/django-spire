from django.urls import path
from django_spire.core.file import views

app_name = 'core_file'

urlpatterns = [
    path('upload/multiple/ajax',
         views.file_multiple_upload_ajax,
         name='upload_multiple_ajax'),

    path('upload/single/ajax',
         views.file_single_upload_ajax,
         name='upload_single_ajax'),
]
