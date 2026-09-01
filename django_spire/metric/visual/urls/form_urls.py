from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.views import form_views
from django_spire.metric.visual.views import region_form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
    path('<int:pk>/delete/', form_views.delete_view, name='delete'),
    path(
        '<int:pk>/conditions/default/',
        form_views.set_default_conditions_view,
        name='set_default_conditions',
    ),
    path('condition/create/', form_views.create_condition_view, name='create_condition'),
    path('condition/<int:pk>/update/', form_views.update_condition_view, name='update_condition'),
    path('condition/<int:pk>/delete/', form_views.delete_condition_view, name='delete_condition'),
    path('reference/create/', form_views.create_reference_view, name='create_reference'),
    path('reference/<int:pk>/update/', form_views.update_reference_view, name='update_reference'),
    path('reference/<int:pk>/delete/', form_views.delete_reference_view, name='delete_reference'),
    path('region/connect/', region_form_views.connect_region_view, name='connect_region'),
    path('region/connect/save/', region_form_views.connect_view, name='connect_region_save'),
    path('region/<int:pk>/update/', region_form_views.update_view, name='update_region'),
    path(
        'region/<int:pk>/disconnect/', region_form_views.disconnect_view, name='disconnect_region'
    ),
]
