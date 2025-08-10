from django.urls import path

from django_spire.knowledge.entry.views import form_views

app_name = 'form'

urlpatterns = [
    path('create/collection/<int:collection_pk>/', form_views.form_view, name='create'),
    path('import/collection/<int:collection_pk>/', form_views.import_form_view, name='import'),
    path('<int:pk>/update/collection/<int:collection_pk>/', form_views.form_view, name='update'),
]
