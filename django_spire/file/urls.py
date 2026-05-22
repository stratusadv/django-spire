from __future__ import annotations

from django.urls import path

from django_spire.file import views


app_name = 'file'

urlpatterns = [
    path('upload/multiple/ajax',
         views.file_upload_ajax_multiple,
         name='upload_ajax_multiple'),

    path('upload/single/ajax',
         views.file_upload_ajax_single,
         name='upload_ajax_single'),
]
