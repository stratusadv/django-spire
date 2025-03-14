from django.urls import path

from module import views


app_name = 'spirechildapp'

urlpatterns = [
    path('<int:pk>/delete/form/', views.spireparentapp_spirechildapp_delete_view, name='delete'),
    path('<int:pk>/delete/form/modal/', views.spireparentapp_spirechildapp_delete_form_modal_view, name='delete_form_modal'),
    path('<int:pk>/detail/', views.spireparentapp_spirechildapp_detail_view, name='detail'),
    path('<int:pk>/form/content/', views.spireparentapp_spirechildapp_form_content_modal_view, name='form_modal_content'),
    path('<int:pk>/form/', views.spireparentapp_spirechildapp_form_view, name='form'),
    path('list/', views.spireparentapp_spirechildapp_list_view, name='list'),
]
