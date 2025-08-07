from django.urls import path

from module.views import form_views

app_name = 'form'
urlpatterns = [
path('<int:pk>/delete/form/', form_views.spireparentapp_spirechildapp_delete_view, name='delete'),
path('<int:pk>/delete/form/modal/', form_views.spireparentapp_spirechildapp_delete_form_modal_view, name='delete_form_modal'),
path('<int:pk>/form/content/', form_views.spireparentapp_spirechildapp_form_content_modal_view, name='form_modal_content'),
path('<int:pk>/form/', form_views.spireparentapp_spirechildapp_form_view, name='form'),
]